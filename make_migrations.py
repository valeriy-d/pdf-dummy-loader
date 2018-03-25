#!/usr/bin/env python3
import sys
from sqlalchemy import create_engine

from settings import settings
from apps.main.models import Base as Users
from apps.pdf_loader.models import Base as Books

registered_models = [
    Users,
    Books
]

engine = create_engine(settings['db'])

for model in registered_models:
    sys.stdout.write('Migrate models\n%s\n' % str(model.metadata.tables))
    model.metadata.create_all(engine)
    sys.stdout.write('Done\n')

sys.stdout.write('Migrations has completed\n')
