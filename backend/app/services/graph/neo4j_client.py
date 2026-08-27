from neo4j import AsyncGraphDatabase
from app.core.config import settings

class Neo4jClient:
    def __init__(self):
        self._driver = None

    async def connect(self):
        self._driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        
    async def close(self):
        if self._driver:
            await self._driver.close()
            
    async def get_supplier_relationships(self, tenant_id: str, supplier_id: str) -> dict:
        """
        Example graph traversal for a given supplier within a tenant.
        """
        if not self._driver:
            return {"error": "Graph DB not connected"}
            
        query = """
        MATCH (s:Supplier {id: $supplier_id, tenant_id: $tenant_id})-[r]-(n)
        RETURN type(r) as relationship, n.id as connected_id, labels(n) as node_type
        """
        
        async with self._driver.session() as session:
            result = await session.run(query, supplier_id=supplier_id, tenant_id=tenant_id)
            records = await result.data()
            
            relationships = []
            risk_signals = 0
            
            for rec in records:
                rel_type = rec["relationship"]
                if rel_type in ["SHARES_ADDRESS", "SHARES_BANK_SIGNAL", "DISPUTED"]:
                    risk_signals += 1
                relationships.append(rec)
                
            return {
                "relationships": relationships,
                "risk_signals": risk_signals,
                "status": "SUCCESS"
            }

neo4j_client = Neo4jClient()
