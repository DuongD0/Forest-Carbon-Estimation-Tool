import uuid
import datetime
import hashlib
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app import crud
import logging

class SerialNumberGenerator:
    """
    VCS-style serial number generator for carbon credits.
    This thing makes unique serial numbers for credit batches.
    """
    
    # example registry code for vietnam
    REGISTRY_CODE = "VNM"
    
    def generate_serial(self, 
                       project_id: str,
                       vintage_year: int,
                       batch_size: float,
                       sequential_number: int) -> str:
        """
        makes a single serial number.
        
        format: [Registry Code]-[Project Hash]-[Vintage Year]-[Batch Size]-[Sequential Number]
        example: VNM-A1B2C3D4-2023-001000-0001
        
        project_id: the project's id.
        vintage_year: year the carbon reduction happened.
        batch_size: how many credits in this batch.
        sequential_number: the number of this batch for this year.
        returns: a vcs-style serial number.
        """
        # use md5 hash for a consistent project code. maybe sha256 later if we need it.
        project_hash = hashlib.md5(str(project_id).encode()).hexdigest()[:8].upper()
        
        # pad numbers to make them all the same length. looks better.
        batch_code = f"{int(batch_size):06d}"
        seq_code = f"{sequential_number:04d}"
        
        serial = f"{self.REGISTRY_CODE}-{project_hash}-{vintage_year}-{batch_code}-{seq_code}"
        
        return serial
    
    def generate_batch_serials(self,
                              db: Session,
                              project_id: str,
                              vintage_year: int,
                              total_credits: float,
                              batch_size: float = 1000.0) -> Dict[str, Any]:
        """
        makes a bunch of serial numbers for a new issuance.
        
        this now checks the database for the last serial number for this project/year
        so we dont make duplicates.

        db: the database session.
        project_id: the project's id.
        vintage_year: the year for the credits.
        total_credits: how many credits we need to make serials for.
        batch_size: how many credits per serial number.
        returns: a dict with all the batch info and serials.
        """
        serials: List[Dict[str, Any]] = []
        remaining_credits = total_credits
        
        # --- db-aware sequential numbering ---
        # get the last sequence number for this project/vintage to avoid collisions.
        try:
            # this assumes we have a function to get the latest sequence number.
            last_sequence = crud.carbon_credit.get_latest_sequential_number(
                db, project_id=project_id, vintage_year=vintage_year
            )
        except Exception as e:
            logging.error(f"Could not retrieve last sequential number for project {project_id}: {e}")
            # depending on what we want, either fail or just start from 0 with a warning.
            # failing is safer.
            raise ValueError("could not get the next sequential number from the db.") from e

        next_sequence = last_sequence + 1
        
        while remaining_credits > 0:
            current_batch_size = min(batch_size, remaining_credits)
            
            serial_str = self.generate_serial(
                project_id=project_id,
                vintage_year=vintage_year,
                batch_size=current_batch_size,
                sequential_number=next_sequence
            )
            
            serials.append({
                'serial': serial_str,
                'batch_size': current_batch_size,
                'sequential_number': next_sequence
            })
            
            remaining_credits -= current_batch_size
            next_sequence += 1
        
        logging.info(f"Generated {len(serials)} serials for project {project_id}, vintage {vintage_year}.")
        
        return {
            'project_id': project_id,
            'vintage_year': vintage_year,
            'total_credits': total_credits,
            'batch_size': batch_size,
            'batch_count': len(serials),
            'serials': serials,
            'generation_date': datetime.datetime.utcnow().isoformat()
        }

serial_generator = SerialNumberGenerator() 