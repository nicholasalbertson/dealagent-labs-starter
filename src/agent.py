#!/usr/bin/env python3
"""
DealAgent Labs - Extended with real data sources.
Integrates:
- MassGIS ArcGIS REST (public, no key) for MA parcel/county records
- ATTOM API (requires ATTOM_API_KEY env var) for property details, sales, AVMs
- LLM extraction (stub for Grok/Claude structured calls on OMs or records)
"""

import os
import json
import requests
from typing import Dict, List, Optional
from urllib.parse import quote

class DealAgent:
    def __init__(self, buy_box: Dict):
        self.buy_box = buy_box
        self.leads = []
        self.attom_key = os.getenv("ATTOM_API_KEY")
        self.massgis_url = "https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/MassachusettsPropertyTaxParcels/FeatureServer/1/query"

    def query_massgis_parcels(self, city: str = "FALL RIVER", limit: int = 50) -> List[Dict]:
        """Query public MassGIS parcel layer for Massachusetts county records."""
        where = f"TOWN_NAME = '{city.upper()}'"
        params = {
            "where": where,
            "outFields": "TOWN_NAME,LOC_ID,OWNER1,SITE_ADDR,BLDG_VAL,LAND_VAL,TOTAL_VAL,YEAR_BUILT,BLDG_AREA,USE_CODE",
            "returnGeometry": "false",
            "f": "json",
            "resultRecordCount": limit
        }
        try:
            resp = requests.get(self.massgis_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("features", [])
        except Exception as e:
            print(f"MassGIS query failed: {e}")
            return []

    def fetch_attom_property(self, address: str) -> Optional[Dict]:
        """Fetch property details from ATTOM API (requires key)."""
        if not self.attom_key:
            return {"error": "ATTOM_API_KEY not set"}
        url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
        headers = {"apikey": self.attom_key, "accept": "application/json"}
        params = {"address": address}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def extract_with_llm(self, text: str, schema: Dict) -> Dict:
        """
        Stub for LLM extraction. In production, call Grok/Claude with structured output.
        Example prompt: extract JSON matching schema from text.
        """
        # Placeholder - replace with actual API call
        return {
            "extracted": True,
            "data": {"note": "Implement with Grok structured output or Claude tool use"},
            "schema_used": schema
        }

    def score_propensity(self, property_data: Dict) -> float:
        """Enhanced scoring using ownership tenure, values, age, etc."""
        score = 0.0
        # From MassGIS or ATTOM fields
        total_val = property_data.get("TOTAL_VAL") or property_data.get("total_value", 0)
        year_built = property_data.get("YEAR_BUILT") or 0
        if total_val and total_val < 500000:  # example distress proxy
            score += 0.2
        if year_built and year_built < 1980:
            score += 0.15
        # Add more signals: ownership years, recent sales, etc. from ATTOM
        return min(score, 1.0)

    def run_pipeline(self, city: str = "FALL RIVER") -> List[Dict]:
        parcels = self.query_massgis_parcels(city)
        scored = []
        for feat in parcels[:20]:  # limit for demo
            attrs = feat.get("attributes", {})
            attrs["propensity_score"] = self.score_propensity(attrs)
            if attrs["propensity_score"] > 0.3:
                # Optionally enrich with ATTOM
                if self.attom_key and attrs.get("SITE_ADDR"):
                    attrs["attom"] = self.fetch_attom_property(attrs["SITE_ADDR"])
                scored.append(attrs)
        self.leads = scored
        return scored

if __name__ == "__main__":
    agent = DealAgent({"markets": ["Fall River, MA"], "asset_class": "commercial"})
    leads = agent.run_pipeline()
    print(json.dumps(leads[:5], indent=2))  # sample
    print(f"Found {len(leads)} potential leads from MassGIS.")
