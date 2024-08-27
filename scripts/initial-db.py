import asyncio
from psu_course_review import config, models

if __name__ == "__main__":
    settings = config.get_settings()
    models.init_db(settings)
    asyncio.run(models.recreate_table())