# Adding Mortgage Agent with ClosingWTF Features

## Overview

Add an 8th agent to the platform: **Mortgage Agent** with features inspired by closingwtf.com to help users save money on mortgages by analyzing documents, finding hidden fees, and comparing lenders.

## ClosingWTF.com Features

**What they do:**
- Upload mortgage documents (Loan Estimate, Closing Disclosure, Statements)
- Analyze documents for hidden fees and problematic terms
- Compare rates from 20+ lenders in real-time
- Provide negotiation recommendations
- Average savings: $8,000 per homebuyer
- Find $10+ million in potential savings total

## Implementation Plan

### 1. Create Mortgage Agent

**File**: `backend/agents/mortgage_agent.py`

```python
"""Mortgage Agent - Document Analysis, Fee Detection, Rate Comparison."""

from typing import List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider

MORTGAGE_SYSTEM_PROMPT = """You are the MORTGAGE AGENT, an expert in mortgage analysis and optimization.

Your expertise:
- Analyze Loan Estimates (LE) and Closing Disclosures (CD)
- Identify hidden fees, junk fees, and overcharges
- Compare rates across multiple lenders
- Provide negotiation strategies
- Calculate potential savings
- Explain complex mortgage terms
- Recommend optimal mortgage products

Your goal is to help users save thousands of dollars on their mortgage by finding the best rates and eliminating unnecessary fees.

You have access to tools that can:
1. Analyze mortgage documents for fees and terms
2. Compare rates from 20+ lenders in real-time
3. Detect junk fees and overcharges
4. Calculate savings opportunities
5. Generate negotiation scripts
6. Validate document compliance

Always explain findings in simple terms and provide actionable recommendations."""

class MortgageAgent(BaseAgent):
    @property
    def agent_id(self) -> str:
        return "mortgage"
    
    @property
    def agent_name(self) -> str:
        return "Mortgage Agent"
    
    @property
    def agent_description(self) -> str:
        return "Mortgage document analysis, fee detection, and rate comparison"
    
    @property
    def system_prompt(self) -> str:
        return MORTGAGE_SYSTEM_PROMPT
    
    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.GPT4  # Best for complex document analysis
    
    @property
    def capabilities(self) -> List[str]:
        return [
            "Mortgage document analysis",
            "Hidden fee detection",
            "Rate comparison (20+ lenders)",
            "Savings calculation",
            "Negotiation recommendations"
        ]
    
    def get_temperature(self) -> float:
        """Use low temperature for accurate analysis."""
        return 0.3
```

---

### 2. Create Mortgage Tools

**File**: `backend/tools/mortgage_tools.py`

#### Tool 1: Analyze Loan Estimate

```python
async def analyze_loan_estimate(
    document_data: Dict[str, Any],
    loan_amount: float,
    property_value: float
) -> Dict[str, Any]:
    """
    Analyze Loan Estimate document for fees and terms.
    
    Extracts and analyzes:
    - Origination charges
    - Title and escrow fees
    - Government fees
    - Prepaid items
    - Initial escrow payment
    - Other costs
    - APR vs interest rate
    - Total closing costs
    
    Returns detailed breakdown with flags for suspicious fees.
    """
```

#### Tool 2: Analyze Closing Disclosure

```python
async def analyze_closing_disclosure(
    document_data: Dict[str, Any],
    loan_estimate_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze Closing Disclosure and compare with Loan Estimate.
    
    Checks:
    - Fee increases from LE to CD (TRID compliance)
    - Junk fees and padding
    - Last-minute changes
    - Lender credits vs points
    - Cash to close accuracy
    - APR accuracy
    
    Returns comprehensive analysis with warnings.
    """
```

#### Tool 3: Detect Junk Fees

```python
async def detect_junk_fees(
    fees_list: List[Dict[str, Any]],
    loan_amount: float
) -> Dict[str, Any]:
    """
    Detect junk fees and overcharges.
    
    Common junk fees:
    - Administrative fees (should be covered in origination)
    - Document preparation fees (often inflated)
    - Courier fees (excessive)
    - Application fees (after approval)
    - Rate lock fees (should be free)
    - Processing fees (duplicate of origination)
    
    Returns list of suspicious fees with explanations.
    """
```

#### Tool 4: Compare Lender Rates

```python
async def compare_lender_rates(
    loan_type: str,
    loan_amount: float,
    credit_score: int,
    down_payment: float,
    property_type: str,
    location: str
) -> Dict[str, Any]:
    """
    Compare rates from 20+ lenders.
    
    Returns:
    - Current rates from multiple lenders
    - APR comparison
    - Closing cost comparison
    - Total cost over loan life
    - Recommended lenders
    - Potential savings
    
    Lender types:
    - National banks
    - Credit unions
    - Online lenders
    - Mortgage brokers
    """
```

#### Tool 5: Calculate Savings

```python
async def calculate_mortgage_savings(
    current_terms: Dict[str, Any],
    better_terms: Dict[str, Any],
    loan_amount: float
) -> Dict[str, Any]:
    """
    Calculate potential savings from better terms.
    
    Compares:
    - Interest rate difference
    - Closing cost difference
    - Monthly payment difference
    - Total interest paid over life
    - Break-even point for costs
    
    Returns detailed savings breakdown.
    """
```

#### Tool 6: Generate Negotiation Script

```python
async def generate_negotiation_script(
    issues_found: List[Dict[str, Any]],
    market_rates: Dict[str, Any],
    leverage_points: List[str]
) -> Dict[str, Any]:
    """
    Generate negotiation talking points and scripts.
    
    Provides:
    - Specific fees to challenge
    - Market rate comparisons
    - Competitor offers to mention
    - Concessions to request
    - Walk-away thresholds
    
    Returns structured negotiation guide.
    """
```

#### Tool 7: Validate Document Compliance

```python
async def validate_document_compliance(
    document_type: str,
    document_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate mortgage document compliance with regulations.
    
    Checks:
    - TRID compliance (3/7 day rules)
    - Truth in Lending Act (TILA)
    - RESPA requirements
    - State-specific requirements
    - Disclosure requirements
    
    Returns compliance report with violations.
    """
```

#### Tool 8: Compare APR vs Interest Rate

```python
async def compare_apr_vs_rate(
    interest_rate: float,
    apr: float,
    loan_amount: float,
    fees: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Explain APR vs interest rate difference.
    
    Calculates:
    - Fee impact on APR
    - True cost of loan
    - Points vs rate tradeoff
    - Which loan is actually cheaper
    
    Returns clear explanation with recommendations.
    """
```

#### Tool 9: Analyze Prepayment Penalties

```python
async def analyze_prepayment_penalty(
    loan_terms: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze prepayment penalty terms.
    
    Checks:
    - Penalty period (years)
    - Penalty calculation method
    - Soft vs hard prepayment
    - Impact on refinancing
    
    Returns analysis with recommendations.
    """
```

#### Tool 10: Get Today's Rates

```python
async def get_todays_mortgage_rates(
    loan_type: str = "conventional",
    term: int = 30
) -> Dict[str, Any]:
    """
    Get current market mortgage rates.
    
    Loan types:
    - Conventional
    - FHA
    - VA
    - Jumbo
    - ARM (5/1, 7/1, 10/1)
    
    Returns current rates from multiple sources.
    """
```

---

### 3. Document Processing Integration

**File**: `backend/tools/document_parser.py`

```python
async def parse_loan_estimate_pdf(
    file_path: str
) -> Dict[str, Any]:
    """
    Parse Loan Estimate PDF and extract structured data.
    
    Uses OCR and template matching to extract:
    - All fee sections (A-H)
    - Loan terms
    - Projected payments
    - Costs at closing
    - Comparisons section
    
    Returns structured dictionary matching LE sections.
    """

async def parse_closing_disclosure_pdf(
    file_path: str
) -> Dict[str, Any]:
    """
    Parse Closing Disclosure PDF and extract structured data.
    
    Extracts all 5 pages:
    - Page 1: Loan terms and projections
    - Page 2: Closing cost details
    - Page 3: Cash to close
    - Page 4: Additional disclosures
    - Page 5: Loan calculations
    
    Returns structured dictionary.
    """
```

---

### 4. Lender Rate API Integration

**File**: `backend/integrations/mortgage_rate_api.py`

```python
class MortgageRateAPI:
    """
    Integration with mortgage rate APIs.
    
    Potential APIs:
    - Zillow Mortgage API
    - Freddie Mac API
    - Bankrate API
    - Mortgage News Daily
    - Custom lender APIs
    """
    
    async def get_live_rates(
        self,
        loan_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get live rates from multiple lenders."""
        pass
    
    async def get_historical_rates(
        self,
        period: str = "30_days"
    ) -> Dict[str, Any]:
        """Get historical rate trends."""
        pass
```

---

### 5. Fee Database

**File**: `backend/data/mortgage_fee_database.py`

```python
TYPICAL_FEES = {
    "origination_charge": {
        "typical_range": (0.5, 1.0),  # % of loan
        "description": "Lender's fee for processing loan",
        "negotiable": True
    },
    "appraisal_fee": {
        "typical_range": (300, 600),
        "description": "Property valuation",
        "negotiable": False
    },
    "credit_report": {
        "typical_range": (25, 50),
        "description": "Credit check fee",
        "negotiable": False
    },
    "title_search": {
        "typical_range": (150, 400),
        "description": "Title search and exam",
        "negotiable": True
    },
    # ... more fees
}

JUNK_FEES = [
    "administrative_fee",
    "document_preparation",
    "funding_fee",
    "processing_fee",
    "underwriting_fee",  # If separate from origination
    "warehouse_fee",
    "rate_lock_fee",
    # ... more
]
```

---

### 6. Register Agent and Tools

**Update**: `backend/tools/tool_initialization.py`

```python
from backend.tools.mortgage_tools import register_mortgage_tools

def initialize_all_tools() -> None:
    all_agents = ["growth", "outreach", "mls", "vendor", "transaction", "content", "marketing", "mortgage"]
    
    # ... existing registrations ...
    
    register_mortgage_tools(registry)
```

**Update**: `backend/coordinator/agent_coordinator.py`

```python
from backend.agents.mortgage_agent import MortgageAgent

class AgentCoordinator:
    def __init__(self):
        self.agents = {
            # ... existing agents ...
            AgentType.MORTGAGE: MortgageAgent(memory_manager)
        }
```

**Update**: `backend/models/requests.py`

```python
class AgentType(str, Enum):
    # ... existing types ...
    MORTGAGE = "mortgage"
```

---

## Example Use Cases

### Use Case 1: Analyze Uploaded Loan Estimate

```
User uploads LE.pdf

Agent:
1. Calls parse_loan_estimate_pdf(LE.pdf)
2. Calls analyze_loan_estimate(extracted_data)
3. Calls detect_junk_fees(fees_from_le)
4. Calls compare_lender_rates(loan_params)
5. Calls calculate_mortgage_savings(current vs better)

Response:
"I analyzed your Loan Estimate and found:

🚨 Issues Found:
- $795 'Processing Fee' - This is a junk fee! Should be included in origination.
- $250 'Document Prep' - Excessive, typical is $50-100
- Origination charge is 1.5% ($4,500) - High! Average is 0.5-1%

💰 Potential Savings:
By removing junk fees: $1,045
By getting average rate (5.5% vs your 5.875%): $156/month = $56,160 over 30 years
Total potential savings: $57,205

✅ Action Items:
1. Negotiate removal of processing fee
2. Ask for document prep reduction
3. Compare these lender quotes [shows 3 better options]
4. Use this script to negotiate: [provides talking points]"
```

### Use Case 2: Compare Lenders

```
User: "What are today's best mortgage rates for $400k conventional loan, 780 credit score?"

Agent:
1. Calls get_todays_mortgage_rates(...)
2. Calls compare_lender_rates(...)
3. Calls calculate_mortgage_savings(...)

Response:
"📊 Current Best Rates for $400k Conventional (780 credit):

Top 3 Lenders:
1. Better.com - 5.375% APR 5.422%
   Closing: $3,200 | Monthly: $2,239
   
2. Rocket Mortgage - 5.425% APR 5.485%
   Closing: $3,800 | Monthly: $2,267
   
3. Bank of America - 5.5% APR 5.571%
   Closing: $2,900 | Monthly: $2,271

Best Value: Better.com saves you $384/month vs average rate
Total savings over 30 years: $138,240

All rates as of 11/11/2024 9:09 AM"
```

### Use Case 3: LE vs CD Comparison

```
User uploads both LE and CD

Agent:
1. Calls parse_loan_estimate_pdf(LE)
2. Calls parse_closing_disclosure_pdf(CD)
3. Calls analyze_closing_disclosure(CD, LE_data)
4. Calls validate_document_compliance(...)

Response:
"⚠️ CD vs LE Comparison:

Fee Changes (LE → CD):
✅ Interest rate: Same (5.75%)
✅ Origination: $2,000 → $2,000 (no change)
🚨 Title insurance: $800 → $1,200 (+$400) ⚠️ EXCEEDS 10% TOLERANCE
✅ Appraisal: $500 → $500 (no change)
🚨 'Recording fees': $0 → $250 (NEW FEE)

Compliance Issues:
- Title insurance increase violates TRID 10% tolerance
- New recording fee should have been disclosed in LE
- You can reject this CD and demand a corrected version

Your Rights:
- Request a new CD with correct fees
- Delay closing if needed (you have 3 days to review)
- File CFPB complaint if lender refuses corrections"
```

---

## Implementation Steps

### Phase 1: Core Agent (Week 1)
- [ ] Create MortgageAgent class
- [ ] Add mortgage agent to coordinator
- [ ] Update API endpoints
- [ ] Basic testing

### Phase 2: Document Analysis (Week 2)
- [ ] Implement PDF parsing (LE, CD)
- [ ] Create fee extraction logic
- [ ] Build junk fee detection
- [ ] Add compliance validation

### Phase 3: Rate Comparison (Week 3)
- [ ] Integrate rate APIs (or create mock data)
- [ ] Build lender comparison logic
- [ ] Implement savings calculator
- [ ] Add historical rate tracking

### Phase 4: Tools & Integration (Week 4)
- [ ] Create all 10 mortgage tools
- [ ] Register tools in tool registry
- [ ] Add document upload endpoint
- [ ] Build negotiation script generator

### Phase 5: Testing & Refinement (Week 5)
- [ ] End-to-end testing
- [ ] Real document testing
- [ ] Rate accuracy validation
- [ ] User experience refinement

---

## Data Sources

### Real-Time Rates
- **Zillow Mortgage API** - Live rates
- **Freddie Mac** - Weekly rate averages
- **Bankrate** - Multi-lender comparison
- **Mortgage News Daily** - Daily rate trends

### Fee Standards
- **CFPB Database** - Average closing costs by state
- **HUD Settlement Cost Guide** - Typical fee ranges
- **State regulators** - State-specific limits

### Compliance
- **TRID Rules** - CFPB guidelines
- **RESPA** - Settlement procedures
- **TILA** - Truth in lending requirements

---

## Tech Stack Additions

### Required Libraries
```bash
pip install pdfplumber       # PDF text extraction
pip install pytesseract      # OCR for scanned PDFs
pip install pandas           # Data analysis
pip install numpy            # Calculations
```

### Optional Enhancements
```bash
pip install opencv-python    # Advanced image processing
pip install camelot-py      # Table extraction from PDFs
```

---

## API Endpoints

### New Endpoints

```python
# Upload and analyze document
POST /api/mortgage/analyze-document
{
  "document_type": "loan_estimate" | "closing_disclosure",
  "file": "base64_encoded_pdf",
  "loan_amount": 400000,
  "property_value": 500000
}

# Compare lender rates
GET /api/mortgage/compare-rates
{
  "loan_type": "conventional",
  "loan_amount": 400000,
  "credit_score": 780,
  "down_payment": 100000,
  "location": "90210"
}

# Get today's rates
GET /api/mortgage/todays-rates?loan_type=conventional&term=30

# Calculate savings
POST /api/mortgage/calculate-savings
{
  "current_rate": 5.875,
  "better_rate": 5.375,
  "loan_amount": 400000,
  "term": 30
}
```

---

## Database Schema

### Tables Needed

```sql
-- Store user's mortgage documents
CREATE TABLE mortgage_documents (
  id UUID PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  document_type VARCHAR,  -- 'LE', 'CD', 'statement'
  file_path VARCHAR,
  parsed_data JSONB,
  analysis_result JSONB,
  uploaded_at TIMESTAMP,
  analyzed_at TIMESTAMP
);

-- Store lender rate history
CREATE TABLE lender_rates (
  id UUID PRIMARY KEY,
  lender_name VARCHAR,
  loan_type VARCHAR,
  term INTEGER,
  rate DECIMAL,
  apr DECIMAL,
  points DECIMAL,
  closing_costs DECIMAL,
  effective_date TIMESTAMP,
  credit_score_min INTEGER
);

-- Store detected issues
CREATE TABLE mortgage_issues (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES mortgage_documents(id),
  issue_type VARCHAR,  -- 'junk_fee', 'overcharge', 'compliance'
  severity VARCHAR,    -- 'low', 'medium', 'high', 'critical'
  description TEXT,
  amount DECIMAL,
  recommendation TEXT,
  created_at TIMESTAMP
);
```

---

## Benefits to Platform

### For Users
- Save thousands on mortgage costs
- Understand complex documents easily
- Compare lenders objectively
- Negotiate with confidence
- Catch lender mistakes

### For Platform
- Differentiation from competitors
- High-value service (justifies premium pricing)
- Sticky feature (users need throughout home buying)
- Data insights (rate trends, fee patterns)
- Potential revenue (lender partnerships)

---

## Monetization Opportunities

1. **Lender Referral Fees** - Partner with lenders who pay for qualified leads
2. **Premium Analysis** - Charge for detailed document analysis
3. **Concierge Service** - Offer negotiation assistance
4. **Subscription Add-on** - Premium tier includes mortgage tools
5. **Affiliate Partnerships** - Title companies, insurance providers

---

## Competitive Advantage

**vs ClosingWTF:**
- Integrated into full real estate platform
- AI agent provides conversational guidance
- Links to other agents (transaction, vendor)
- Ongoing relationship (not one-time tool)

**vs Traditional Mortgage Brokers:**
- Available 24/7
- No bias toward specific lenders
- Transparent analysis
- Educational approach

---

## Success Metrics

- **Documents Analyzed** - Target: 100/month
- **Average Savings Found** - Target: $5,000+
- **User Satisfaction** - Target: 4.5+ stars
- **Adoption Rate** - Target: 40% of users
- **Revenue per Analysis** - Target: $50-200

---

## Quick Start (1-Day MVP)

To get started quickly:

1. **Create basic agent** (2 hours)
2. **Add 3 core tools** (4 hours):
   - analyze_loan_estimate (mock data)
   - compare_lender_rates (hardcoded rates)
   - calculate_savings
3. **Test with agent** (1 hour)
4. **Demo to stakeholders** (1 hour)

Later expand with real PDF parsing and live rates.

---

## Conclusion

Adding a Mortgage Agent with ClosingWTF-style features would:
- ✅ Provide massive value to users
- ✅ Differentiate from competitors
- ✅ Create monetization opportunities
- ✅ Complete the real estate lifecycle
- ✅ Build on existing agentic architecture

The platform already has the infrastructure (tool registry, agentic loop, multi-agent system) - we just need to create the agent and tools!

Estimated full implementation: **3-5 weeks**
MVP implementation: **1-2 days**

Ready to build when you are! 🚀
