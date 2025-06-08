from sqlalchemy.orm import Session
from app.models.project import Project, ProjectType
from app.models.ecosystem import Ecosystem
from app.services.forest_detector import ForestAreaDetector
from app import crud
from geoalchemy2.shape import to_shape

class CarbonCreditCalculator:
    """
    A service to calculate carbon credits for different project types.
    - For Forestry projects, it uses forest area detection and ecosystem factors.
    - For Renewable Energy projects, it uses generation data and grid emission factors.
    """
    def __init__(self, db: Session):
        self.db = db

    def _get_project_area_ha(self, project: Project) -> float:
        """Calculate project area in hectares from its geometry."""
        if not project.location_geometry:
            raise ValueError("Project geometry is not set.")
        
        project_shape = to_shape(project.location_geometry)
        # Assumes CRS is in meters (e.g., a UTM projection). 
        # For geographic coordinates (lat/lon), this needs reprojection for accurate area.
        area_m2 = project_shape.area
        return area_m2 / 10000

    def calculate_forestry_credits(self, project: Project, image_path: str) -> float:
        """Calculates carbon credits for a forestry project."""
        if not project.ecosystem_id:
            raise ValueError("Project does not have an associated ecosystem.")
        
        ecosystem = crud.ecosystem.get(self.db, id=project.ecosystem_id)
        if not ecosystem:
            raise ValueError(f"Ecosystem with id {project.ecosystem_id} not found.")

        total_area_ha = self._get_project_area_ha(project)
        
        # Use ForestAreaDetector to find the forested percentage
        detector = ForestAreaDetector(image_path)
        forest_percentage = detector.detect_forest_area()
        
        forested_area_ha = total_area_ha * forest_percentage
        
        # Simplified calculation: credits = area * carbon_factor
        # A real model would be more complex (e.g., growth over time, biomass equations).
        carbon_credits = forested_area_ha * ecosystem.carbon_factor
        
        return carbon_credits

    def calculate_renewable_energy_credits(self, project: Project) -> float:
        """Calculates carbon credits for a renewable energy project."""
        # This requires details specific to renewable energy projects
        renewable_details = crud.renewable_energy_project.get_by_project_id(self.db, project_id=project.id)
        if not renewable_details:
            raise ValueError("Renewable energy project details not found.")

        # Credits = Annual Generation (MWh) * Grid Emission Factor (tCO2e/MWh)
        carbon_credits = renewable_details.annual_generation_mwh * renewable_details.grid_emission_factor
        return carbon_credits

    def calculate_credits(self, project: Project, image_path: str | None = None) -> float:
        """
        Calculates carbon credits based on the project type.
        """
        if project.project_type == ProjectType.FORESTRY:
            if not image_path:
                raise ValueError("Image path is required for forestry projects.")
            return self.calculate_forestry_credits(project, image_path)
        
        elif project.project_type == ProjectType.RENEWABLE_ENERGY:
            return self.calculate_renewable_energy_credits(project)
            
        else:
            raise ValueError(f"Unsupported project type: {project.project_type}") 