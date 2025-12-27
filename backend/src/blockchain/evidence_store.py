import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List
import ipfshttpclient
from web3 import Web3
import uuid

class BlockchainEvidenceStore:
    """Immutable evidence storage using IPFS and Hyperledger"""
    
    def __init__(self):
        # Initialize IPFS client
        self.ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
        
        # Initialize Hyperledger Fabric connection
        self.hyperledger_config = {
            'network_config': './connection-profile.yaml',
            'channel_name': 'evidencechannel',
            'chaincode_name': 'evidencecc',
            'wallet_path': './wallet'
        }
        
    def store_evidence(self, evidence_data: Dict[str, Any]) -> Dict[str, str]:
        """Store evidence in blockchain with auto-tagging"""
        
        # Generate unique evidence ID
        evidence_id = str(uuid.uuid4())
        
        # Create evidence metadata
        metadata = {
            'evidence_id': evidence_id,
            'timestamp': datetime.utcnow().isoformat(),
            'type': evidence_data.get('type', 'unknown'),
            'source': evidence_data.get('source', 'user_upload'),
            'hash': self._calculate_hash(evidence_data['content'])
        }
        
        # Auto-tag evidence
        metadata['auto_tags'] = self._auto_tag_evidence(evidence_data)
        
        # Store in IPFS
        ipfs_hash = self._store_in_ipfs({
            'metadata': metadata,
            'content': evidence_data['content']
        })
        
        metadata['ipfs_hash'] = ipfs_hash
        
        # Store reference in Hyperledger
        tx_id = self._store_in_hyperledger({
            'evidence_id': evidence_id,
            'ipfs_hash': ipfs_hash,
            'content_hash': metadata['hash'],
            'timestamp': metadata['timestamp'],
            'tags': metadata['auto_tags']
        })
        
        metadata['hyperledger_tx_id'] = tx_id
        
        return {
            'evidence_id': evidence_id,
            'ipfs_hash': ipfs_hash,
            'hyperledger_tx_id': tx_id,
            'content_hash': metadata['hash'],
            'timestamp': metadata['timestamp'],
            'tags': metadata['auto_tags']
        }
    
    def _store_in_ipfs(self, data: Dict) -> str:
        """Store data in IPFS and return hash"""
        # Convert to JSON string
        json_data = json.dumps(data, ensure_ascii=False)
        
        # Add to IPFS
        result = self.ipfs_client.add_str(json_data)
        
        return result
    
    def _store_in_hyperledger(self, evidence_record: Dict) -> str:
        """Store evidence record in Hyperledger Fabric"""
        # This would connect to Hyperledger network
        # For demo, generate mock transaction ID
        tx_id = f"HL_TX_{hashlib.sha256(json.dumps(evidence_record).encode()).hexdigest()[:32]}"
        
        # In production, this would submit transaction to Hyperledger
        # client = HyperledgerClient(self.hyperledger_config)
        # tx_id = client.submit_transaction('storeEvidence', evidence_record)
        
        return tx_id
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _auto_tag_evidence(self, evidence_data: Dict) -> List[str]:
        """Automatically tag evidence based on content"""
        tags = []
        content = evidence_data.get('content', '').lower()
        evidence_type = evidence_data.get('type', '')
        
        # Content-based tagging
        if evidence_type == 'chat_log':
            tags.append('chat_log')
            if any(word in content for word in ['threat', 'kill', 'harm']):
                tags.append('threat_contained')
            if any(word in content for word in ['bully', 'harass', 'abuse']):
                tags.append('bullying')
        
        elif evidence_type == 'screenshot':
            tags.append('screenshot')
            if 'violence' in content:
                tags.append('violent_content')
            if 'explicit' in content:
                tags.append('explicit_content')
        
        elif evidence_type == 'email':
            tags.append('email')
            if 'phishing' in content:
                tags.append('phishing_attempt')
            if 'scam' in content:
                tags.append('scam')
        
        # Add timestamp tag
        tags.append(f"timestamp_{datetime.utcnow().strftime('%Y%m%d')}")
        
        return tags
    
    def verify_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """Verify evidence integrity using blockchain"""
        # Retrieve from Hyperledger
        # evidence_record = client.query_chaincode('getEvidence', evidence_id)
        
        # For demo, return mock data
        return {
            'evidence_id': evidence_id,
            'verified': True,
            'tamper_proof': True,
            'timestamp': datetime.utcnow().isoformat(),
            'blockchain_confirmations': 12
        }
