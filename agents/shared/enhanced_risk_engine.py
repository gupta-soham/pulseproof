"""
Enhanced Risk Engine for PulseProof Multi-Agent System
Integrates advanced blockchain security analysis with real-time data
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Web3 integration for real-time blockchain data
try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logging.warning("Web3 not available. Install with: pip install web3")

from models import ProcessedEvent, SuspicionLevel, EventType
from config import Config


class RiskCategory(Enum):
    """Risk categories for comprehensive assessment"""
    FINANCIAL_IMPACT = "financial_impact"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    REPUTATION_RISK = "reputation_risk"
    HISTORICAL_CONTEXT = "historical_context"
    APPROVAL_RISK = "approval_risk"


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment result"""
    overall_score: float
    confidence: float
    risk_category: RiskCategory
    factors: List[str]
    recommendation: str
    details: Dict[str, Any]


class EnhancedRiskEngine:
    """
    Enhanced risk assessment engine with real-time blockchain data integration
    """
    
    def __init__(self, web3_provider_url: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Web3 connection
        self.web3 = None
        web3_url = web3_provider_url or Config.get_web3_provider_url()
        if WEB3_AVAILABLE and web3_url:
            try:
                self.web3 = Web3(Web3.HTTPProvider(web3_url))
                if self.web3.is_connected():
                    self.logger.info("✅ Web3 connected successfully")
                else:
                    self.logger.warning("⚠️ Web3 connection failed")
                    self.web3 = None
            except Exception as e:
                self.logger.error(f"❌ Web3 initialization error: {e}")
                self.web3 = None
        
        # Risk assessment weights from config
        self.risk_weights = {
            RiskCategory.FINANCIAL_IMPACT: Config.RISK_WEIGHTS['financial_impact'],
            RiskCategory.BEHAVIORAL_ANOMALY: Config.RISK_WEIGHTS['behavioral_anomaly'],
            RiskCategory.REPUTATION_RISK: Config.RISK_WEIGHTS['reputation_risk'],
            RiskCategory.HISTORICAL_CONTEXT: Config.RISK_WEIGHTS['historical_context'],
            RiskCategory.APPROVAL_RISK: Config.RISK_WEIGHTS['approval_risk']
        }
        
        # Risk thresholds from config
        self.MIN_CONFIDENCE = Config.MIN_CONFIDENCE
        self.HIGH_RISK_THRESHOLD = Config.HIGH_RISK_THRESHOLD
        self.CRITICAL_RISK_THRESHOLD = Config.CRITICAL_RISK_THRESHOLD
        
        # External API configurations from config
        self.etherscan_api_key = Config.ETHERSCAN_API_KEY
        self.etherscan_api_url = Config.ETHERSCAN_API_URL
        self.coingecko_api_url = Config.COINGECKO_API_URL
        self.goplus_api_url = Config.GOPLUS_API_URL
        
        # Cache for performance optimization
        self._price_cache = {}
        self._reputation_cache = {}
        self._cache_ttl = Config.CACHE_TTL
        
    def assess_comprehensive_risk(self, processed_event: ProcessedEvent) -> RiskAssessment:
        """
        Perform comprehensive risk assessment on a processed event
        
        Args:
            processed_event: Preprocessed event data
            
        Returns:
            RiskAssessment: Comprehensive risk analysis
        """
        try:
            self.logger.info(f"🔍 Starting comprehensive risk assessment for {processed_event.transaction_hash[:10]}...")
            
            # Initialize risk components
            risk_components = {}
            confidence_factors = []
            all_factors = []
            
            # 1. Financial Impact Analysis
            financial_risk = self._analyze_financial_impact(processed_event)
            risk_components[RiskCategory.FINANCIAL_IMPACT] = financial_risk
            confidence_factors.append(financial_risk['confidence'])
            all_factors.extend(financial_risk.get('factors', []))
            
            # 2. Behavioral Anomaly Detection
            anomaly_risk = self._detect_behavioral_anomalies(processed_event)
            risk_components[RiskCategory.BEHAVIORAL_ANOMALY] = anomaly_risk
            confidence_factors.append(anomaly_risk['confidence'])
            all_factors.extend(anomaly_risk.get('factors', []))
            
            # 3. Reputation Risk Assessment
            reputation_risk = self._assess_reputation_risk(processed_event)
            risk_components[RiskCategory.REPUTATION_RISK] = reputation_risk
            confidence_factors.append(reputation_risk['confidence'])
            all_factors.extend(reputation_risk.get('factors', []))
            
            # 4. Historical Context Analysis
            historical_risk = self._analyze_historical_context(processed_event)
            risk_components[RiskCategory.HISTORICAL_CONTEXT] = historical_risk
            confidence_factors.append(historical_risk['confidence'])
            all_factors.extend(historical_risk.get('factors', []))
            
            # 5. Approval Risk Analysis (if applicable)
            if processed_event.event_type == EventType.APPROVAL:
                approval_risk = self._analyze_approval_risk(processed_event)
                risk_components[RiskCategory.APPROVAL_RISK] = approval_risk
                confidence_factors.append(approval_risk['confidence'])
                all_factors.extend(approval_risk.get('factors', []))
            
            # Calculate weighted overall risk score
            overall_score = self._calculate_weighted_risk_score(risk_components)
            overall_confidence = sum(confidence_factors) / len(confidence_factors)
            
            # Determine primary risk category
            primary_category = max(risk_components.items(), key=lambda x: x[1]['score'])[0]
            
            # Generate recommendation
            recommendation = self._generate_recommendation(overall_score, overall_confidence)
            
            # Create comprehensive assessment
            assessment = RiskAssessment(
                overall_score=overall_score,
                confidence=overall_confidence,
                risk_category=primary_category,
                factors=list(set(all_factors)),  # Remove duplicates
                recommendation=recommendation,
                details={
                    'risk_components': risk_components,
                    'confidence_factors': confidence_factors,
                    'assessment_timestamp': datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"✅ Risk assessment completed - Score: {overall_score:.2f}, Confidence: {overall_confidence:.2f}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"❌ Error in comprehensive risk assessment: {e}")
            return RiskAssessment(
                overall_score=0.5,
                confidence=0.1,
                risk_category=RiskCategory.FINANCIAL_IMPACT,
                factors=[f"Assessment error: {str(e)}"],
                recommendation="INVESTIGATE",
                details={'error': str(e)}
            )
    
    def _analyze_financial_impact(self, event: ProcessedEvent) -> Dict[str, Any]:
        """
        Analyze real financial impact using on-chain data and token prices
        """
        try:
            parsed_data = event.parsed_data
            factors = []
            score = 0.0
            confidence = 0.5
            
            # Get transaction value
            if 'amount' in parsed_data:
                amount = parsed_data['amount']
                token_address = event.contract_address
                
                # Calculate USD value
                usd_value = self._calculate_usd_value(amount, token_address)
                
                # Risk scoring based on USD value using config thresholds
                if usd_value >= Config.CRITICAL_FINANCIAL_THRESHOLD:  # $1M+
                    score, confidence = 1.0, 0.9
                    factors.append("CRITICAL_FINANCIAL_IMPACT")
                elif usd_value >= Config.HIGH_FINANCIAL_THRESHOLD:  # $100K+
                    score, confidence = 0.8, 0.8
                    factors.append("HIGH_FINANCIAL_IMPACT")
                elif usd_value >= Config.MEDIUM_FINANCIAL_THRESHOLD:   # $10K+
                    score, confidence = 0.6, 0.7
                    factors.append("MEDIUM_FINANCIAL_IMPACT")
                elif usd_value >= Config.LOW_FINANCIAL_THRESHOLD:    # $1K+
                    score, confidence = 0.4, 0.6
                    factors.append("LOW_FINANCIAL_IMPACT")
                else:
                    score, confidence = 0.2, 0.5
                    factors.append("MINIMAL_FINANCIAL_IMPACT")
                
                return {
                    'score': score,
                    'confidence': confidence,
                    'factors': factors,
                    'usd_value': usd_value,
                    'amount': amount,
                    'token_address': token_address
                }
            
            return {'score': 0.3, 'confidence': 0.3, 'factors': ['NO_AMOUNT_DATA']}
            
        except Exception as e:
            self.logger.error(f"Error in financial impact analysis: {e}")
            return {'score': 0.3, 'confidence': 0.3, 'factors': [f'Analysis error: {str(e)}']}
    
    def _calculate_usd_value(self, amount: int, token_address: str) -> float:
        """
        Calculate USD value of token amount
        """
        try:
            # Check cache first
            cache_key = f"{token_address}_{amount}"
            if cache_key in self._price_cache:
                cached_data = self._price_cache[cache_key]
                if datetime.now().timestamp() - cached_data['timestamp'] < self._cache_ttl:
                    return cached_data['usd_value']
            
            # Get token price
            token_price = self._get_token_price(token_address)
            
            # Estimate decimals (simplified - in production, fetch from contract)
            decimals = 18  # Most ERC-20 tokens use 18 decimals
            
            # Calculate USD value
            token_amount = amount / (10 ** decimals)
            usd_value = token_amount * token_price
            
            # Cache the result
            self._price_cache[cache_key] = {
                'usd_value': usd_value,
                'timestamp': datetime.now().timestamp()
            }
            
            return usd_value
            
        except Exception as e:
            self.logger.error(f"Error calculating USD value: {e}")
            return 0.0
    
    def _get_token_price(self, token_address: str) -> float:
        """
        Get token price from CoinGecko API
        """
        try:
            # Check cache first
            if token_address in self._price_cache:
                cached_data = self._price_cache[token_address]
                if datetime.now().timestamp() - cached_data['timestamp'] < self._cache_ttl:
                    return cached_data['price']
            
            # Special handling for common tokens
            if token_address.lower() == '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2':  # WETH
                response = requests.get(f'{self.coingecko_api_url}/simple/price?ids=ethereum&vs_currencies=usd')
                if response.status_code == 200:
                    price = response.json()['ethereum']['usd']
                    self._price_cache[token_address] = {'price': price, 'timestamp': datetime.now().timestamp()}
                    return price
            
            # Generic token price lookup
            response = requests.get(f'{self.coingecko_api_url}/simple/token_price/ethereum?contract_addresses={token_address}&vs_currencies=usd')
            if response.status_code == 200:
                data = response.json()
                if token_address.lower() in data:
                    price = data[token_address.lower()]['usd']
                    self._price_cache[token_address] = {'price': price, 'timestamp': datetime.now().timestamp()}
                    return price
            
            # Fallback price
            return 1.0
            
        except Exception as e:
            self.logger.error(f"Error getting token price: {e}")
            return 1.0
    
    def _detect_behavioral_anomalies(self, event: ProcessedEvent) -> Dict[str, Any]:
        """
        Detect behavioral anomalies based on historical patterns
        """
        try:
            # Extract address for analysis
            parsed_data = event.parsed_data
            from_address = parsed_data.get('from_address', '')
            
            if not from_address:
                return {'score': 0.3, 'confidence': 0.3, 'factors': ['NO_FROM_ADDRESS']}
            
            # Get historical behavior (simplified for now)
            historical_behavior = self._get_historical_behavior(from_address)
            current_behavior = self._extract_behavioral_features(event)
            
            # Calculate anomaly score
            anomaly_score = self._calculate_anomaly_score(historical_behavior, current_behavior)
            confidence = self._calculate_anomaly_confidence(anomaly_score, len(historical_behavior.get('transactions', [])))
            
            factors = []
            if anomaly_score > 0.7:
                factors.append("HIGH_ANOMALY_SCORE")
            elif anomaly_score > 0.4:
                factors.append("MEDIUM_ANOMALY_SCORE")
            else:
                factors.append("LOW_ANOMALY_SCORE")
            
            return {
                'score': anomaly_score,
                'confidence': confidence,
                'factors': factors,
                'anomalies_detected': self._identify_specific_anomalies(historical_behavior, current_behavior)
            }
            
        except Exception as e:
            self.logger.error(f"Error in behavioral anomaly detection: {e}")
            return {'score': 0.3, 'confidence': 0.3, 'factors': [f'Analysis error: {str(e)}']}
    
    def _get_historical_behavior(self, address: str) -> Dict[str, Any]:
        """
        Get historical transaction behavior for an address using Etherscan API
        """
        try:
            # Check cache first
            cache_key = f"historical_{address}"
            if cache_key in self._reputation_cache:
                cached_data = self._reputation_cache[cache_key]
                if datetime.now().timestamp() - cached_data['timestamp'] < self._cache_ttl:
                    return cached_data['data']
            
            self.logger.info(f"🔍 Fetching historical behavior for {address[:10]}...")
            
            # Get transaction list from Etherscan
            response = requests.get(
                f"{self.etherscan_api_url}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={self.etherscan_api_key}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    transactions = data['result'][-100:]  # Last 100 transactions
                    
                    # Analyze transaction patterns
                    total_txs = len(transactions)
                    if total_txs == 0:
                        return {'transaction_count': 0, 'average_value': 0, 'unique_contracts': 0, 'transactions': []}
                    
                    # Calculate average value (in wei)
                    total_value = sum(int(tx.get('value', 0)) for tx in transactions)
                    avg_value = total_value / total_txs
                    
                    # Count unique contract interactions
                    unique_contracts = len(set(tx.get('to', '') for tx in transactions if tx.get('to')))
                    
                    # Get first and last transaction timestamps
                    first_seen = transactions[0].get('timeStamp') if transactions else None
                    last_seen = transactions[-1].get('timeStamp') if transactions else None
                    
                    # Calculate transaction frequency
                    if first_seen and last_seen:
                        time_span = int(last_seen) - int(first_seen)
                        frequency = total_txs / max(time_span / 86400, 1)  # transactions per day
                    else:
                        frequency = 0
                    
                    historical_data = {
                        'transaction_count': total_txs,
                        'average_value': avg_value,
                        'unique_contracts': unique_contracts,
                        'transactions': transactions,
                        'first_seen': first_seen,
                        'last_seen': last_seen,
                        'frequency_per_day': frequency,
                        'total_value': total_value
                    }
                    
                    # Cache the result
                    self._reputation_cache[cache_key] = {
                        'data': historical_data,
                        'timestamp': datetime.now().timestamp()
                    }
                    
                    self.logger.info(f"✅ Historical data retrieved: {total_txs} transactions, {unique_contracts} contracts")
                    return historical_data
                else:
                    self.logger.warning(f"⚠️ Etherscan API returned no data for {address[:10]}")
                    return {'transaction_count': 0, 'average_value': 0, 'unique_contracts': 0, 'transactions': []}
            else:
                self.logger.error(f"❌ Etherscan API error: {response.status_code}")
                return {'transaction_count': 0, 'average_value': 0, 'unique_contracts': 0, 'transactions': []}
                
        except Exception as e:
            self.logger.error(f"Error getting historical behavior: {e}")
            return {'transaction_count': 0, 'average_value': 0, 'unique_contracts': 0, 'transactions': []}
    
    def _extract_behavioral_features(self, event: ProcessedEvent) -> Dict[str, Any]:
        """
        Extract behavioral features from current event
        """
        parsed_data = event.parsed_data
        return {
            'value': parsed_data.get('amount', 0),
            'event_type': event.event_type.value,
            'timestamp': datetime.now().timestamp(),
            'contract_address': event.contract_address
        }
    
    def _calculate_anomaly_score(self, historical: Dict, current: Dict) -> float:
        """
        Calculate comprehensive anomaly score based on deviation from historical patterns
        """
        score = 0.0
        
        # 1. Value anomaly (most important)
        historical_avg_value = historical.get('average_value', 0)
        current_value = current.get('value', 0)
        
        if historical_avg_value > 0:
            value_ratio = current_value / historical_avg_value
            if value_ratio > 1000:  # 1000x historical average
                score += 0.9
            elif value_ratio > 100:  # 100x historical average
                score += 0.7
            elif value_ratio > 10:   # 10x historical average
                score += 0.5
            elif value_ratio > 2:    # 2x historical average
                score += 0.2
        
        # 2. Contract interaction anomaly
        historical_contracts = set(tx.get('to', '') for tx in historical.get('transactions', []))
        current_contract = current.get('contract_address', '')
        
        if current_contract and current_contract not in historical_contracts:
            # New contract interaction
            if len(historical_contracts) > 0:
                score += 0.3  # Penalty for new contract
            else:
                score += 0.1  # First interaction
        
        # 3. Frequency anomaly
        historical_frequency = historical.get('frequency_per_day', 0)
        if historical_frequency > 0:
            # If this is a high-frequency user, sudden large transaction is more suspicious
            if historical_frequency > 10:  # High-frequency user
                if value_ratio > 10:
                    score += 0.2
        
        # 4. Account age anomaly
        first_seen = historical.get('first_seen')
        if first_seen:
            account_age_days = (datetime.now().timestamp() - int(first_seen)) / 86400
            if account_age_days < 1:  # New account
                if current_value > 1000000000000000000:  # > 1 ETH
                    score += 0.4
            elif account_age_days < 7:  # Week-old account
                if current_value > 10000000000000000000:  # > 10 ETH
                    score += 0.3
        
        # 5. Transaction count anomaly
        transaction_count = historical.get('transaction_count', 0)
        if transaction_count == 0:  # First transaction
            if current_value > 1000000000000000000:  # > 1 ETH
                score += 0.5
        elif transaction_count < 5:  # Very new account
            if value_ratio > 50:
                score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_anomaly_confidence(self, anomaly_score: float, historical_data_points: int) -> float:
        """
        Calculate confidence based on anomaly score and data quality
        """
        base_confidence = anomaly_score * 0.8
        
        if historical_data_points > 50:
            data_quality_factor = 1.0
        elif historical_data_points > 10:
            data_quality_factor = 0.7
        elif historical_data_points > 0:
            data_quality_factor = 0.4
        else:
            data_quality_factor = 0.1
        
        return min(base_confidence * data_quality_factor, 1.0)
    
    def _identify_specific_anomalies(self, historical: Dict, current: Dict) -> List[str]:
        """
        Identify specific types of anomalies
        """
        anomalies = []
        
        # Check for value anomaly
        if self._is_value_anomaly(historical, current):
            anomalies.append("UNUSUAL_VALUE")
        
        # Check for timing anomaly
        if self._is_timing_anomaly(current):
            anomalies.append("UNUSUAL_TIMING")
        
        return anomalies
    
    def _is_value_anomaly(self, historical: Dict, current: Dict) -> bool:
        """Check if current value is anomalous compared to historical average"""
        avg_value = historical.get('average_value', 0)
        current_value = current.get('value', 0)
        return current_value > avg_value * 10 and avg_value > 0
    
    def _is_timing_anomaly(self, current: Dict) -> bool:
        """Check if transaction timing is unusual"""
        current_time = current.get('timestamp', 0)
        if current_time == 0:
            return False
        
        dt = datetime.fromtimestamp(current_time)
        # Check if transaction is during unusual hours (2 AM - 6 AM)
        return 2 <= dt.hour <= 6
    
    def _assess_reputation_risk(self, event: ProcessedEvent) -> Dict[str, Any]:
        """
        Assess reputation risk using security databases
        """
        try:
            parsed_data = event.parsed_data
            from_address = parsed_data.get('from_address', '')
            
            if not from_address:
                return {'score': 0.3, 'confidence': 0.3, 'factors': ['NO_FROM_ADDRESS']}
            
            # Check cache first
            if from_address in self._reputation_cache:
                cached_data = self._reputation_cache[from_address]
                if datetime.now().timestamp() - cached_data['timestamp'] < self._cache_ttl:
                    return cached_data['risk_data']
            
            # Check reputation using GoPlus API (simplified for now)
            reputation_risk = self._check_address_reputation(from_address)
            
            # Cache the result
            self._reputation_cache[from_address] = {
                'risk_data': reputation_risk,
                'timestamp': datetime.now().timestamp()
            }
            
            return reputation_risk
            
        except Exception as e:
            self.logger.error(f"Error in reputation risk assessment: {e}")
            return {'score': 0.3, 'confidence': 0.3, 'factors': [f'Analysis error: {str(e)}']}
    
    def _check_address_reputation(self, address: str) -> Dict[str, Any]:
        """
        Check address reputation using GoPlus security API
        """
        try:
            # Check cache first
            cache_key = f"reputation_{address}"
            if cache_key in self._reputation_cache:
                cached_data = self._reputation_cache[cache_key]
                if datetime.now().timestamp() - cached_data['timestamp'] < self._cache_ttl:
                    return cached_data['data']
            
            self.logger.info(f"🔍 Checking reputation for {address[:10]}...")
            
            # Check address security using GoPlus API
            response = requests.get(
                f"{self.goplus_api_url}/address_security/{address}",
                timeout=10
            )
            
            if response.status_code == 200:
                security_data = response.json()
                result = security_data.get('result', {})
                
                # Define risk weights for different security indicators
                risk_indicators = {
                    'cybercrime': 0.9,
                    'money_laundering': 0.9,
                    'financial_crime': 0.8,
                    'sanctioned': 0.9,
                    'stealing_attack': 0.8,
                    'phishing_activities': 0.8,
                    'blackmail_activities': 0.7,
                    'darkweb_transactions': 0.7,
                    'mixer': 0.6,
                    'honeypot_related_address': 0.7,
                    'malicious_mining_activities': 0.6,
                    'blacklist_doubt': 0.8,
                    'fake_kyc': 0.5,
                    'fake_standard_interface': 0.5,
                    'fake_token': 0.4,
                    'gas_abuse': 0.4,
                    'number_of_malicious_contracts_created': 0.6,
                    'reinit': 0.3
                }
                
                max_risk_score = 0.0
                triggered_factors = []
                
                # Check each security indicator
                for indicator, weight in risk_indicators.items():
                    value = result.get(indicator, "0")
                    try:
                        indicator_value = int(value) if isinstance(value, str) else value
                        if indicator_value > 0:
                            max_risk_score = max(max_risk_score, weight)
                            # Create human-readable factor names
                            factor_name = indicator.replace('_', ' ').title().replace('Kyc', 'KYC')
                            triggered_factors.append(factor_name)
                    except (ValueError, TypeError):
                        continue
                
                # Special handling for high-risk indicators
                critical_indicators = ['cybercrime', 'money_laundering', 'financial_crime', 'sanctioned']
                for critical in critical_indicators:
                    if int(result.get(critical, "0")) > 0:
                        triggered_factors.insert(0, f"CRITICAL: {critical.replace('_', ' ').title()}")
                        max_risk_score = max(max_risk_score, 0.95)
                
                # Calculate confidence based on data quality
                confidence = 0.9 if triggered_factors else 0.8
                
                reputation_data = {
                    'score': max_risk_score,
                    'confidence': confidence,
                    'factors': triggered_factors if triggered_factors else ['No reputation issues found'],
                    'security_data': result
                }
                
                # Cache the result
                self._reputation_cache[cache_key] = {
                    'data': reputation_data,
                    'timestamp': datetime.now().timestamp()
                }
                
                if triggered_factors:
                    self.logger.warning(f"⚠️ Reputation issues found: {len(triggered_factors)} factors")
                else:
                    self.logger.info(f"✅ No reputation issues found")
                
                return reputation_data
            
            else:
                self.logger.error(f"❌ GoPlus API error: {response.status_code}")
                return {'score': 0.2, 'confidence': 0.3, 'factors': [f'API error: {response.status_code}']}
                
        except Exception as e:
            self.logger.error(f"Error checking address reputation: {e}")
            return {'score': 0.2, 'confidence': 0.3, 'factors': [f'Reputation check failed: {str(e)}']}
    
    def _analyze_historical_context(self, event: ProcessedEvent) -> Dict[str, Any]:
        """
        Analyze comprehensive historical context for additional risk factors
        """
        try:
            parsed_data = event.parsed_data
            from_address = parsed_data.get('from_address', '')
            
            if not from_address:
                return {'score': 0.3, 'confidence': 0.3, 'factors': ['NO_FROM_ADDRESS']}
            
            # Get historical behavior data
            historical_behavior = self._get_historical_behavior(from_address)
            
            risk_factors = []
            risk_score = 0.0
            
            # 1. Account age analysis
            first_seen = historical_behavior.get('first_seen')
            if first_seen:
                account_age_days = (datetime.now().timestamp() - int(first_seen)) / 86400
                if account_age_days < 1:
                    risk_score += 0.3
                    risk_factors.append("NEW_ACCOUNT")
                elif account_age_days < 7:
                    risk_score += 0.2
                    risk_factors.append("VERY_NEW_ACCOUNT")
                elif account_age_days < 30:
                    risk_score += 0.1
                    risk_factors.append("RECENT_ACCOUNT")
            
            # 2. Transaction history analysis
            transaction_count = historical_behavior.get('transaction_count', 0)
            if transaction_count == 0:
                risk_score += 0.4
                risk_factors.append("NO_TRANSACTION_HISTORY")
            elif transaction_count < 5:
                risk_score += 0.2
                risk_factors.append("MINIMAL_TRANSACTION_HISTORY")
            elif transaction_count > 1000:
                risk_score += 0.1
                risk_factors.append("HIGH_FREQUENCY_USER")
            
            # 3. Contract interaction analysis
            unique_contracts = historical_behavior.get('unique_contracts', 0)
            if unique_contracts == 0:
                risk_score += 0.2
                risk_factors.append("NO_CONTRACT_INTERACTIONS")
            elif unique_contracts > 100:
                risk_score += 0.1
                risk_factors.append("MANY_CONTRACT_INTERACTIONS")
            
            # 4. Value pattern analysis
            total_value = historical_behavior.get('total_value', 0)
            current_value = parsed_data.get('amount', 0)
            
            if total_value > 0:
                value_ratio = current_value / total_value
                if value_ratio > 0.5:  # Current transaction is >50% of total historical value
                    risk_score += 0.3
                    risk_factors.append("LARGE_VALUE_RATIO")
            
            # 5. Frequency analysis
            frequency = historical_behavior.get('frequency_per_day', 0)
            if frequency > 50:  # Very high frequency
                risk_score += 0.1
                risk_factors.append("VERY_HIGH_FREQUENCY")
            elif frequency == 0 and transaction_count > 0:
                risk_score += 0.2
                risk_factors.append("INACTIVE_ACCOUNT")
            
            # Calculate confidence based on data quality
            confidence = 0.8 if transaction_count > 10 else 0.6 if transaction_count > 0 else 0.4
            
            return {
                'score': min(risk_score, 1.0),
                'confidence': confidence,
                'factors': risk_factors if risk_factors else ['STANDARD_HISTORICAL_CONTEXT'],
                'historical_summary': {
                    'account_age_days': account_age_days if first_seen else None,
                    'transaction_count': transaction_count,
                    'unique_contracts': unique_contracts,
                    'frequency_per_day': frequency
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in historical context analysis: {e}")
            return {'score': 0.3, 'confidence': 0.3, 'factors': [f'Analysis error: {str(e)}']}
    
    def _analyze_approval_risk(self, event: ProcessedEvent) -> Dict[str, Any]:
        """
        Analyze approval-specific risks
        """
        try:
            parsed_data = event.parsed_data
            factors = []
            score = 0.0
            
            # Check for unlimited approval
            if 'approval_amount' in parsed_data:
                approval_amount = parsed_data['approval_amount']
                if self._is_unlimited_approval(approval_amount):
                    score = 0.9
                    factors.append("UNLIMITED_APPROVAL")
                elif approval_amount > 10**24:  # Very large approval
                    score = 0.7
                    factors.append("LARGE_APPROVAL")
                else:
                    score = 0.3
                    factors.append("NORMAL_APPROVAL")
            
            return {
                'score': score,
                'confidence': 0.8,
                'factors': factors
            }
            
        except Exception as e:
            self.logger.error(f"Error in approval risk analysis: {e}")
            return {'score': 0.3, 'confidence': 0.3, 'factors': [f'Analysis error: {str(e)}']}
    
    def _is_unlimited_approval(self, amount: int) -> bool:
        """Check if approval amount is effectively unlimited"""
        unlimited_values = [
            2**256 - 1,
            115792089237316195423570985008687907853269984665640564039457584007913129639935
        ]
        return amount in unlimited_values or amount > 10**30
    
    def _calculate_weighted_risk_score(self, risk_components: Dict[RiskCategory, Dict]) -> float:
        """
        Calculate weighted overall risk score
        """
        total_score = 0.0
        total_weight = 0.0
        
        for category, component in risk_components.items():
            weight = self.risk_weights.get(category, 0.0)
            score = component.get('score', 0.0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / max(total_weight, 0.001)  # Avoid division by zero
    
    def _generate_recommendation(self, risk_score: float, confidence: float) -> str:
        """
        Generate recommendation based on risk score and confidence
        """
        if confidence < self.MIN_CONFIDENCE:
            return "MONITOR"
        elif risk_score >= self.CRITICAL_RISK_THRESHOLD:
            return "CRITICAL_INVESTIGATION"
        elif risk_score >= self.HIGH_RISK_THRESHOLD:
            return "IMMEDIATE_INVESTIGATION"
        elif risk_score >= 0.5:
            return "INVESTIGATE"
        else:
            return "MONITOR"
