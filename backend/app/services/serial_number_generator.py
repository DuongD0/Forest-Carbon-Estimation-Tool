import datetime
from app.models.project import Project
from app.models.carbon_credit import CarbonCredit

class SerialNumberGenerator:
    """
    Generates VCS-compliant serial numbers for carbon credits.
    Format: [Registry]-[Project ID]-[Vintage Year]-[Block Start]-[Block End]-[Credit Type]
    Example: VC-PROJ123-2023-1-1000-TCO2
    """

    def __init__(self, registry_prefix: str = "VC"):
        self.registry_prefix = registry_prefix

    def _get_next_block(self, project_id: str, vintage_year: int) -> tuple[int, int]:
        """
        Determines the next available serial number block for a project's vintage.
        NOTE: This is a simplified placeholder. A real implementation would need
        to query the database for the last issued serial number for this project/vintage
        and increment it.
        """
        # For this example, we'll assume each issuance is a new block of 1000.
        # This part needs a robust, atomic way to get the next block sequence.
        # This might involve a separate database table or a transaction with row-level locking.
        
        # Placeholder logic:
        # last_credit = db.query(CarbonCredit)...filter by project_id and vintage...
        # start = last_credit.block_end + 1 if last_credit else 1
        
        start = 1 # Placeholder
        return start, 1000 # Placeholder

    def generate(self, project: Project, vintage_year: int, quantity: int) -> str:
        """
        Generates a new serial number for a block of credits.
        """
        project_code = f"PROJ{str(project.id)[:8].upper()}"
        
        # For simplicity, we use the quantity to define the block range.
        # A real system might have more complex block management.
        block_start = 1
        block_end = quantity

        credit_type = "TCO2" # Tons of Carbon Dioxide Equivalent

        serial_number = (
            f"{self.registry_prefix}-"
            f"{project_code}-"
            f"{vintage_year}-"
            f"{block_start}-"
            f"{block_end}-"
            f"{credit_type}"
        )
        return serial_number

serial_number_generator = SerialNumberGenerator() 