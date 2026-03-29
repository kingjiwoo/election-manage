from neo4j import AsyncGraphDatabase

from app.core.config import settings

driver = AsyncGraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
)


async def get_neo4j_session():
    async with driver.session() as session:
        yield session


async def close_driver():
    await driver.close()
