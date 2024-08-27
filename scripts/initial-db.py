import sys
from pathlib import Path

# Add the parent directory of 'psu_course_review' to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from psu_course_review import config, models

import asyncio


if __name__ == "__main__":
    settings = config.get_settings()
    models.init_db(settings)
    asyncio.run(models.recreate_table())
