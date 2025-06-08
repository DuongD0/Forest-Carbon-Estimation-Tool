import uuid
import datetime
import hashlib
from typing import Dict, Any

class SerialNumberGenerator:
    """
    VCS-compliant serial number generator for carbon credits
    """
    
    # Registry code for Vietnam Carbon Registry
    REGISTRY_CODE = "VNM"
    
    def generate_serial(self, 
                       project_id: str,
                       vintage_year: int,
                       batch_size: float,
                       sequential_number: int) -> str:
        """
        Generate VCS-compliant serial number
        
        Parameters:
        - project_id: Unique project identifier
        - vintage_year: Year of carbon credit vintage
        - batch_size: Size of credit batch in tCO2e
        - sequential_number: Sequential issuance number
        
        Returns:
        - VCS-compliant serial number
        """
        # Format: VNM-[Project ID]-[Vintage Year]-[Batch Size]-[Sequential Number]
        project_hash = hashlib.md5(str(project_id).encode()).hexdigest()[:8]
        batch_code = f"{int(batch_size):06d}"
        seq_code = f"{sequential_number:04d}"
        
        serial = f"{self.REGISTRY_CODE}-{project_hash.upper()}-{vintage_year}-{batch_code}-{seq_code}"
        
        return serial
    
    def generate_batch_serials(self,
                              project_id: str,
                              vintage_year: int,
                              total_credits: float,
                              batch_size: float = 1000) -> Dict[str, Any]:
        """
        Generate a batch of serial numbers for a project
        
        Parameters:
        - project_id: Unique project identifier
        - vintage_year: Year of carbon credit vintage
        - total_credits: Total credits to generate serials for
        - batch_size: Size of each credit batch
        
        Returns:
        - Dictionary with batch information and serials
        """
        serials = []
        remaining = total_credits
        batch_count = 0
        
        while remaining > 0:
            batch_count += 1
            current_batch = min(batch_size, remaining)
            
            serial = self.generate_serial(
                project_id=project_id,
                vintage_year=vintage_year,
                batch_size=current_batch,
                sequential_number=batch_count
            )
            
            serials.append({
                'serial': serial,
                'batch_size': current_batch,
                'sequential_number': batch_count
            })
            
            remaining -= current_batch
        
        return {
            'project_id': project_id,
            'vintage_year': vintage_year,
            'total_credits': total_credits,
            'batch_size': batch_size,
            'batch_count': batch_count,
            'serials': serials,
            'generation_date': datetime.datetime.utcnow().isoformat()
        }

serial_generator = SerialNumberGenerator() 