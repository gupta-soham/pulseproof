import re
from hyperon import MeTTa, E, S, ValueAtom

class POCRAG:
    def __init__(self, metta_instance: MeTTa):
        self.metta = metta_instance

    def query_domain_pocs(self, domain):
        """Find POC types suitable for a domain (defi, nft, security, blockchain)."""
        domain = domain.strip('"')
        query_str = f'!(match &self (domain_poc {domain} $poc_type) $poc_type)'
        results = self.metta.run(query_str)
        print(f"Domain POCs query: {query_str}")
        print(f"Domain POCs results: {results}")

        unique_pocs = list(set(str(r[0]) for r in results if r and len(r) > 0)) if results else []
        return unique_pocs

    def get_poc_architecture(self, poc_type):
        """Get architecture pattern for a POC type."""
        poc_type = poc_type.strip('"')
        query_str = f'!(match &self (poc_architecture {poc_type} $architecture) $architecture)'
        results = self.metta.run(query_str)
        print(f"POC Architecture query: {query_str}")
        print(f"POC Architecture results: {results}")
        
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_poc_implementation_steps(self, poc_type):
        """Get implementation steps for a POC type."""
        poc_type = poc_type.strip('"')
        query_str = f'!(match &self (poc_steps {poc_type} $steps) $steps)'
        results = self.metta.run(query_str)
        print(f"POC Steps query: {query_str}")
        print(f"POC Steps results: {results}")

        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_poc_code_template(self, poc_type):
        """Get code template for a POC type."""
        poc_type = poc_type.strip('"')
        query_str = f'!(match &self (poc_code {poc_type} $code) $code)'
        results = self.metta.run(query_str)
        print(f"POC Code query: {query_str}")
        print(f"POC Code results: {results}")

        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_complexity_level(self, poc_type):
        """Get implementation complexity for a POC type."""
        poc_type = poc_type.strip('"')
        query_str = f'!(match &self (complexity_level {poc_type} $complexity) $complexity)'
        results = self.metta.run(query_str)
        print(f"Complexity query: {query_str}")
        print(f"Complexity results: {results}")

        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_development_time(self, poc_type):
        """Get estimated development time for a POC type."""
        poc_type = poc_type.strip('"')
        query_str = f'!(match &self (development_time {poc_type} $time) $time)'
        results = self.metta.run(query_str)
        print(f"Development time query: {query_str}")
        print(f"Development time results: {results}")

        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def query_risk_pattern_poc(self, risk_pattern):
        """Find POC recommendations for specific risk patterns."""
        risk_pattern = risk_pattern.strip('"')
        query_str = f'!(match &self (risk_pattern_poc {risk_pattern} $poc) $poc)'
        results = self.metta.run(query_str)
        print(f"Risk pattern POC query: {query_str}")
        print(f"Risk pattern POC results: {results}")

        return [str(r[0]) for r in results if r and len(r) > 0] if results else []

    def query_threat_poc(self, threat_type):
        """Find POC recommendations for specific threat types."""
        threat_type = threat_type.strip('"')
        query_str = f'!(match &self (threat_poc {threat_type} $poc) $poc)'
        results = self.metta.run(query_str)
        print(f"Threat POC query: {query_str}")
        print(f"Threat POC results: {results}")

        return [str(r[0]) for r in results if r and len(r) > 0] if results else []

    def query_poc_faq(self, question):
        """Retrieve POC FAQ answers."""
        query_str = f'!(match &self (poc_faq "{question}" $answer) $answer)'
        results = self.metta.run(query_str)
        print(f"POC FAQ query: {query_str}")
        print(f"POC FAQ results: {results}")

        return results[0][0].get_object().value if results and results[0] else None

    def find_best_poc_for_requirements(self, requirements, domain):
        """Find the best POC type based on requirements and domain using MeTTa reasoning."""
        
        # First get all POCs for the domain
        domain_pocs = self.query_domain_pocs(domain)
        
        if not domain_pocs:
            return None
        
        # Simple keyword matching to find best POC
        requirements_lower = requirements.lower()
        
        # Priority keywords for different POC types
        poc_keywords = {
            "risk_monitoring_dashboard": ["monitor", "dashboard", "alert", "real-time", "risk"],
            "authenticity_verification_system": ["authentic", "verify", "fake", "verification"],
            "smart_contract_analyzer": ["contract", "vulnerability", "security", "audit"],
            "transaction_anomaly_detector": ["anomaly", "suspicious", "unusual", "pattern"],
            "flash_loan_attack_monitor": ["flash loan", "attack", "exploit"],
        }
        
        best_poc = None
        max_matches = 0
        
        for poc in domain_pocs:
            if poc in poc_keywords:
                matches = sum(1 for keyword in poc_keywords[poc] if keyword in requirements_lower)
                if matches > max_matches:
                    max_matches = matches
                    best_poc = poc
        
        # If no keyword matches, return the first domain POC
        return best_poc or domain_pocs[0]

    def add_knowledge(self, relation_type, subject, object_value):
        """Add new POC knowledge dynamically."""
        if isinstance(object_value, str):
            object_value = ValueAtom(object_value)
        self.metta.space().add_atom(E(S(relation_type), S(subject), object_value))
        return f"Added {relation_type}: {subject} → {object_value}"