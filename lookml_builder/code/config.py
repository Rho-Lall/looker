"""
Configuration management for LookerExploreBuilder
Handles YAML configuration files for custom classifications and business rules
"""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ClassificationConfig:
    """Configuration for custom field classifications"""
    exclude_from_filters: List[str] = field(default_factory=list)  # Fields that should NOT have filters
    force_as_measures: List[str] = field(default_factory=list)     # Fields that should be measures
    force_as_flags: List[str] = field(default_factory=list)        # Fields that should be flags
    force_as_ids: List[str] = field(default_factory=list)          # Fields that should be IDs
    primary_key: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassificationConfig':
        """Create ClassificationConfig from dictionary"""
        return cls(
            exclude_from_filters=data.get('exclude_from_filters', []),
            force_as_measures=data.get('force_as_measures', []),
            force_as_flags=data.get('force_as_flags', []),
            force_as_ids=data.get('force_as_ids', []),
            primary_key=data.get('primary_key')
        )


@dataclass
class FormattingConfig:
    """Configuration for field formatting rules"""
    currency_patterns: List[str] = field(default_factory=lambda: ["revenue", "cost", "earning", "amount", "price"])
    percentage_patterns: List[str] = field(default_factory=lambda: ["rate", "percent", "pct"])
    count_patterns: List[str] = field(default_factory=lambda: ["count", "total", "num"])
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormattingConfig':
        """Create FormattingConfig from dictionary"""
        return cls(
            currency_patterns=data.get('currency_patterns', cls().currency_patterns),
            percentage_patterns=data.get('percentage_patterns', cls().percentage_patterns),
            count_patterns=data.get('count_patterns', cls().count_patterns)
        )


@dataclass
class LookerConfig:
    """Main configuration class for LookerExploreBuilder"""
    classification: ClassificationConfig = field(default_factory=ClassificationConfig)
    formatting: FormattingConfig = field(default_factory=FormattingConfig)
    ontology: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LookerConfig':
        """Create LookerConfig from dictionary"""
        return cls(
            classification=ClassificationConfig.from_dict(data.get('classification', {})),
            formatting=FormattingConfig.from_dict(data.get('formatting', {})),
            ontology=data.get('ontology', {})
        )
    
    @classmethod
    def from_yaml_file(cls, config_path: str) -> 'LookerConfig':
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        return cls.from_dict(data)
    
    @classmethod
    def get_default_config(cls) -> 'LookerConfig':
        """Get default configuration"""
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'classification': {
                'exclude_from_filters': self.classification.exclude_from_filters,
                'force_as_measures': self.classification.force_as_measures,
                'force_as_flags': self.classification.force_as_flags,
                'force_as_ids': self.classification.force_as_ids,
                'primary_key': self.classification.primary_key
            },
            'formatting': {
                'currency_patterns': self.formatting.currency_patterns,
                'percentage_patterns': self.formatting.percentage_patterns,
                'count_patterns': self.formatting.count_patterns
            },
            'ontology': self.ontology
        }
    
    def save_to_yaml(self, config_path: str) -> None:
        """Save configuration to YAML file"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)


def create_sample_config(output_path: str = "looker_config.yaml") -> str:
    """Create a sample configuration file with examples and documentation"""
    
    sample_config = {
        'classification': {
            'exclude_from_filters': [
                'internal_notes',  # Example: Don't create filters for internal notes
                'raw_data'         # Example: Don't create filters for raw data fields
            ],
            'force_as_measures': [
                'transaction_count',  # Example: Force transaction_count to be a measure
                'avg_amount'         # Example: Force avg_amount to be a measure
            ],
            'force_as_flags': [
                'status_code',     # Example: Numeric status_code should be a flag, not measure
                'priority_level'   # Example: Numeric priority_level should be a flag, not measure
            ],
            'force_as_ids': [
                'external_ref',    # Example: String external_ref should be an ID, not dimension
                'tracking_number'  # Example: String tracking_number should be an ID, not dimension
            ],
            'primary_key': 'transaction_id'  # Example: Override primary key detection
        },
        'formatting': {
            'currency_patterns': [
                'revenue', 'cost', 'earning', 'amount', 'price', 'fee', 'charge'
            ],
            'percentage_patterns': [
                'rate', 'percent', 'pct', 'ratio'
            ],
            'count_patterns': [
                'count', 'total', 'num', 'quantity', 'qty'
            ]
        },
        'ontology': {
            'project': {
                'name': 'sample_project',
                'governance_status': 'in_development'
            },
            'relationships': [
                {
                    'from': 'financial_transactions',
                    'to': 'customers',
                    'type': 'left_outer',
                    'relationship': 'many_to_one',
                    'via': '${financial_transactions.customer_id} = ${customers.id}'
                }
            ]
        }
    }
    
    # Add comments to the YAML file
    yaml_content = f"""# Looker Explore Builder Configuration
# This file defines custom classification rules and formatting preferences

# Custom field classifications
# Override automatic detection by specifying fields in these lists
classification:
  # Fields that should NOT have filter dimensions created
  exclude_from_filters:
    {yaml.dump(sample_config['classification']['exclude_from_filters'], default_flow_style=False, indent=4).replace('- ', '    - ').strip()}
  
  # Fields that should be treated as measures (even if they're strings)
  force_as_measures:
    {yaml.dump(sample_config['classification']['force_as_measures'], default_flow_style=False, indent=4).replace('- ', '    - ').strip()}
  
  # Numeric fields that should be flags instead of measures
  force_as_flags:
    {yaml.dump(sample_config['classification']['force_as_flags'], default_flow_style=False, indent=4).replace('- ', '    - ').strip()}
  
  # String fields that should be IDs instead of dimensions
  force_as_ids:
    {yaml.dump(sample_config['classification']['force_as_ids'], default_flow_style=False, indent=4).replace('- ', '    - ').strip()}
  
  # Override primary key detection (optional)
  primary_key: {sample_config['classification']['primary_key']}

# Formatting rules for measures
# Fields matching these patterns will get appropriate value_format
formatting:
  # Patterns for currency formatting ($#,##0.00)
  currency_patterns:
    {yaml.dump(sample_config['formatting']['currency_patterns'], default_flow_style=False, indent=4).replace('- ', '    - ').strip()}
  
  # Patterns for percentage formatting (0.00%)
  percentage_patterns:
    {yaml.dump(sample_config['formatting']['percentage_patterns'], default_flow_style=False, indent=4).replace('- ', '    - ').strip()}
  
  # Patterns for count formatting (#,##0)
  count_patterns:
    {yaml.dump(sample_config['formatting']['count_patterns'], default_flow_style=False, indent=4).replace('- ', '    - ').strip()}

# Ontology configuration for explore relationships
ontology:
{yaml.dump(sample_config['ontology'], default_flow_style=False, indent=2).strip()}
"""
    
    with open(output_path, 'w') as f:
        f.write(yaml_content)
    
    return output_path