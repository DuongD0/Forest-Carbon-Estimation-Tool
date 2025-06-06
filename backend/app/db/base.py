# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa

# User Management Models
from app.models.user import User, Role, Permission  # noqa

# Project Management Models
from app.models.project import Project # noqa
# Assuming Project model exists and is correctly defined

# Spatial Models
from app.models.forest import Forest # noqa
from app.models.forest_plot import ForestPlot # noqa - New model
from app.models.plot_composition import PlotComposition # noqa - New model
from app.models.imagery import Imagery # noqa - Existing model

# Reference Models
from app.models.tree_species import TreeSpecies # noqa - New model
# Assuming AllometricEquation model exists or will be created/updated
# from app.models.allometric_equation import AllometricEquation # noqa

# Calculation Models
from app.models.biomass import Biomass # noqa - New or updated model
from app.models.carbon_stock import CarbonStock # noqa - New or updated model
from app.models.baseline import Baseline # noqa - New or updated model
from app.models.carbon_credit import CarbonCredit # noqa - New or updated model

print("Base models imported for Alembic discovery.")

