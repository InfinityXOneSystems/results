# Lead Sniper Validation Framework

## Objective

Validate that 100% of property and business data is accurate, verifiable, and supported by documented proof of truth.

---

## Validation Layers

### Layer 1: Address Validation

**Purpose:** Ensure property addresses are real, valid, and properly formatted

**Validation Methods:**

1. **USPS Address Verification**
   - API: USPS Address Standardization API
   - Validates address format
   - Confirms delivery capability
   - Returns standardized address
   - Confidence score: 99%

2. **Google Maps Geocoding**
   - API: Google Maps Geocoding API
   - Converts address to coordinates
   - Verifies address exists
   - Returns place type (residential, commercial, etc.)
   - Confidence score: 98%

3. **County Assessor Cross-Reference**
   - Database: County Property Appraiser
   - Confirms property exists in county records
   - Returns parcel number
   - Returns property details
   - Confidence score: 99%

4. **Tax Assessor Verification**
   - Database: County Tax Assessor
   - Confirms property on tax roll
   - Returns assessed value
   - Returns owner information
   - Confidence score: 99%

**Validation Logic:**
```
IF address_valid_usps AND address_valid_google AND address_in_county_records THEN
  address_validation_score = 99
  validation_status = "VERIFIED"
ELSE IF address_valid_usps AND address_valid_google THEN
  address_validation_score = 95
  validation_status = "LIKELY_VALID"
ELSE IF address_valid_usps OR address_valid_google THEN
  address_validation_score = 80
  validation_status = "NEEDS_REVIEW"
ELSE
  address_validation_score = 0
  validation_status = "INVALID"
END IF
```

---

### Layer 2: Property Ownership Verification

**Purpose:** Confirm current property owner and ownership history

**Validation Methods:**

1. **County Deed Records**
   - Source: County Clerk/Recorder
   - Document Type: Deed
   - Information: Owner name, ownership date, deed type
   - Proof: PDF copy of recorded deed
   - Confidence score: 99%

2. **Tax Assessor Records**
   - Source: County Tax Assessor
   - Information: Current owner, mailing address, tax ID
   - Proof: Property record card screenshot
   - Confidence score: 98%

3. **Property Appraiser Database**
   - Source: County Property Appraiser
   - Information: Owner, property details, assessed value
   - Proof: Property record screenshot
   - Confidence score: 98%

4. **Title Company Records**
   - Source: Title Insurance Company
   - Information: Title history, liens, encumbrances
   - Proof: Title report
   - Confidence score: 99%

**Validation Logic:**
```
IF owner_in_deed_records AND owner_in_tax_records AND owner_in_appraiser_records THEN
  ownership_validation_score = 99
  validation_status = "VERIFIED"
ELSE IF owner_in_deed_records AND owner_in_tax_records THEN
  ownership_validation_score = 95
  validation_status = "LIKELY_VALID"
ELSE IF owner_in_deed_records OR owner_in_tax_records THEN
  ownership_validation_score = 80
  validation_status = "NEEDS_REVIEW"
ELSE
  ownership_validation_score = 0
  validation_status = "UNVERIFIED"
END IF
```

---

### Layer 3: Distress Indicator Verification

**Purpose:** Confirm that property is actually distressed and matches claimed distress type

**Validation Methods:**

#### 3A: Foreclosure Verification

**Sources:**
1. HUD Foreclosure Database
   - Proof: HUD listing screenshot
   - Confidence: 99%

2. County Clerk Records
   - Proof: Notice of Default/Foreclosure PDF
   - Confidence: 99%

3. Court Records
   - Proof: Court case filing screenshot
   - Confidence: 99%

4. Foreclosure Auction Sites
   - Proof: Auction listing screenshot
   - Confidence: 98%

**Validation Logic:**
```
IF foreclosure_in_hud_database AND foreclosure_notice_filed THEN
  foreclosure_validation_score = 99
ELSE IF foreclosure_in_hud_database OR foreclosure_notice_filed THEN
  foreclosure_validation_score = 90
ELSE
  foreclosure_validation_score = 0
END IF
```

#### 3B: Tax Lien Verification

**Sources:**
1. County Tax Collector
   - Proof: Tax lien certificate PDF
   - Confidence: 99%

2. Tax Assessor Records
   - Proof: Delinquent tax list screenshot
   - Confidence: 98%

3. Public Records Databases
   - Proof: Lien search results
   - Confidence: 95%

**Validation Logic:**
```
IF tax_lien_in_county_records AND lien_amount_matches AND lien_date_valid THEN
  tax_lien_validation_score = 99
ELSE IF tax_lien_in_county_records THEN
  tax_lien_validation_score = 90
ELSE
  tax_lien_validation_score = 0
END IF
```

#### 3C: Bank-Owned Property Verification

**Sources:**
1. County Deed Records
   - Proof: Deed showing bank ownership
   - Confidence: 99%

2. Real Estate Listings
   - Proof: Zillow/Redfin listing showing "Bank-owned"
   - Confidence: 95%

3. Bank Records
   - Proof: Bank website listing
   - Confidence: 98%

**Validation Logic:**
```
IF bank_in_deed_records AND bank_listed_as_owner THEN
  bank_owned_validation_score = 99
ELSE IF bank_in_deed_records OR bank_listed_as_owner THEN
  bank_owned_validation_score = 90
ELSE
  bank_owned_validation_score = 0
END IF
```

#### 3D: Probate Property Verification

**Sources:**
1. Court Records
   - Proof: Probate case filing PDF
   - Confidence: 99%

2. County Clerk Records
   - Proof: Probate notice screenshot
   - Confidence: 98%

3. Estate Sale Listings
   - Proof: Estate sale listing screenshot
   - Confidence: 90%

**Validation Logic:**
```
IF probate_case_filed AND property_in_probate_estate THEN
  probate_validation_score = 99
ELSE IF probate_case_filed OR property_in_probate_estate THEN
  probate_validation_score = 85
ELSE
  probate_validation_score = 0
END IF
```

---

### Layer 4: Price & Value Verification

**Purpose:** Confirm that list price and estimated value are accurate

**Validation Methods:**

1. **Comparable Sales Analysis**
   - Compare to recent sales in area
   - Adjust for property differences
   - Calculate market value range
   - Confidence: 90%

2. **County Assessor Valuation**
   - Use official assessed value
   - Compare to list price
   - Flag significant discrepancies
   - Confidence: 95%

3. **Real Estate Platform Data**
   - Zillow Zestimate
   - Redfin estimate
   - MLS comparable sales
   - Confidence: 85%

4. **Appraisal Records**
   - Bank appraisals
   - Tax appraisals
   - Insurance appraisals
   - Confidence: 95%

**Validation Logic:**
```
estimated_value_range = [assessed_value * 0.9, assessed_value * 1.1]
comparable_value_range = [comp_sales_avg * 0.85, comp_sales_avg * 1.15]

IF list_price < estimated_value_range.min THEN
  price_validation_score = 95
  status = "UNDERPRICED"
ELSE IF list_price IN estimated_value_range THEN
  price_validation_score = 80
  status = "FAIRLY_PRICED"
ELSE IF list_price > estimated_value_range.max THEN
  price_validation_score = 60
  status = "OVERPRICED"
END IF
```

---

### Layer 5: Business Data Verification

**Purpose:** Confirm business information is accurate and loan eligibility is valid

**Validation Methods:**

1. **Secretary of State Registration**
   - Verify business exists
   - Confirm registration status
   - Check filing dates
   - Confidence: 99%

2. **Business License Verification**
   - Confirm active license
   - Verify license type
   - Check expiration date
   - Confidence: 98%

3. **Credit Report Review**
   - Business credit score
   - Payment history
   - Debt obligations
   - Confidence: 95%

4. **Financial Statement Analysis**
   - Revenue verification
   - Profit/loss analysis
   - Cash flow assessment
   - Confidence: 90%

5. **Industry Verification**
   - Confirm industry classification
   - Verify business type
   - Check industry trends
   - Confidence: 85%

**Validation Logic:**
```
IF business_registered AND license_active AND credit_score > 650 THEN
  business_validation_score = 95
  loan_eligibility = "HIGH"
ELSE IF business_registered AND license_active THEN
  business_validation_score = 80
  loan_eligibility = "MEDIUM"
ELSE IF business_registered OR license_active THEN
  business_validation_score = 60
  loan_eligibility = "LOW"
ELSE
  business_validation_score = 0
  loan_eligibility = "INELIGIBLE"
END IF
```

---

## Proof of Truth Collection

### Document Requirements

For each property, collect:

1. **Address Proof**
   - USPS verification screenshot
   - Google Maps screenshot
   - County assessor record

2. **Ownership Proof**
   - Deed record (PDF)
   - Tax assessor record (screenshot)
   - Property appraiser record (screenshot)

3. **Distress Proof** (varies by type)
   - Foreclosure: Notice of Default + HUD listing
   - Tax Lien: Tax lien certificate + delinquent tax list
   - Bank-Owned: Deed showing bank ownership + listing
   - Probate: Court filing + probate notice

4. **Value Proof**
   - County assessed value
   - Comparable sales data
   - Recent appraisal (if available)

5. **Source Attribution**
   - URL of data source
   - Access timestamp
   - Screenshot/PDF of source
   - Extraction method

---

## Validation Scoring

### Overall Validation Score

```
validation_score = (
  address_validation_score * 0.25 +
  ownership_validation_score * 0.25 +
  distress_validation_score * 0.30 +
  price_validation_score * 0.15 +
  source_attribution_score * 0.05
)

IF validation_score >= 95 THEN
  validation_status = "VERIFIED"
ELSE IF validation_score >= 85 THEN
  validation_status = "LIKELY_VALID"
ELSE IF validation_score >= 75 THEN
  validation_status = "NEEDS_REVIEW"
ELSE
  validation_status = "INVALID"
END IF
```

---

## Validation Workflow

```
1. Extract property data from source
2. Validate address (Layer 1)
3. Verify ownership (Layer 2)
4. Confirm distress (Layer 3)
5. Verify price/value (Layer 4)
6. Collect proof documents
7. Calculate validation score
8. Flag for manual review if score < 85
9. Generate validation report
10. Archive all proof documents
```

---

## Quality Assurance

### Manual Review Process

Properties with validation score < 85 are manually reviewed:

1. **Data Analyst Review**
   - Examine all validation results
   - Research property history
   - Contact county if needed
   - Make final determination

2. **Supervisor Approval**
   - Review analyst findings
   - Approve or reject property
   - Document decision
   - Archive decision record

3. **Audit Trail**
   - Record all review steps
   - Timestamp all actions
   - Document all findings
   - Maintain complete history

---

## Reporting

### Validation Report

For each property, generate:

1. **Validation Summary**
   - Overall score
   - Validation status
   - Key findings
   - Recommendations

2. **Detailed Results**
   - Address validation results
   - Ownership verification results
   - Distress confirmation results
   - Price verification results

3. **Proof of Truth**
   - List of documents collected
   - Document sources
   - Document timestamps
   - Document URLs

4. **Audit Trail**
   - Validation steps taken
   - Timestamps
   - Analyst notes
   - Approval status

---

## Continuous Improvement

### Validation Metrics

- **Accuracy Rate:** % of properties validated correctly
- **False Positive Rate:** % of invalid properties marked as valid
- **False Negative Rate:** % of valid properties marked as invalid
- **Processing Time:** Average time per property
- **Manual Review Rate:** % requiring manual review

### Algorithm Refinement

- Monitor validation accuracy
- Adjust scoring weights
- Update validation sources
- Improve automation
- Reduce manual review rate

---

## Implementation

See implementation files in `/validators/` directory for code examples.
