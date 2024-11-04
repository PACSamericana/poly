import json

RADIOLOGY_ABBREVIATIONS = {
    "hydro": "hydronephrosis",
    "hetero": "heterogeneous",
    "calc": "calcification",
    "calcs": "calcifications",
    "AP": "anteroposterior",
    "sig": "signifcant",
    "approx": "approximately",
}

# Preprocessing (Categorization) Example

PREPROCESSING_EXAMPLE = {
    "input": """low density subcentimeter left hepatic lobe cyst too small, mild right hydro, bladder wall thickening, 3.2x4.5x9.0 cm right adnexal mass increased from prior previously 2.4 x 2.3 x 2.3 cm (Series 4, image 76) increased 12 mm aortocaval lymph node previously 7mm, chronic L1 endplate fracture""",
    
    "output": {
        "liver": [
            {
                "finding": "low density subcentimeter left hepatic lobe cyst too small",
                "series": None,
                "image": None
            }
        ],
        "kidneys_and_ureters": [
            {
                "finding": "mild right hydro",
                "series": None,
                "image": None
            }
        ],
        "urinary_bladder": [
            {
                "finding": "bladder wall thickening",
                "series": None,
                "image": None
            }
        ],
        "reproductive": [
            {
                "finding": "3.2x4.5x9.0 cm right adnexal mass increased from prior previously 2.4 x 2.3 x 2.3 cm",
                "series": "4",
                "image": "76"
            }
        ],
        "lymph_nodes": [
            {
                "finding": "increased 12 mm aortocaval lymph node previously 7mm",
                "series": None,
                "image": None
            }
        ],
        "bones": [
            {
                "finding": "chronic L1 endplate fracture",
                "series": None,
                "image": None
            }
        ]
    }
}

# Section Processing Examples

SECTION_PROCESSING_EXAMPLES = {
    "liver": {
        "template": "Normal size and attenuation with smooth surface contour. No focal hepatic lesions. Portal and hepatic veins are patent.",
        "finding": "low density subcentimeter left hepatic lobe cyst too small",
        "output": "The liver is normal in size with smooth surface contour. There is a subcentimeter low-density cyst in the left hepatic lobe. Portal and hepatic veins are patent."
    },
    
    "kidneys_and_ureters": {
        "template": "Normal-sized kidneys with symmetric enhancement. No hydronephrosis or renal stones.",
        "finding": "mild right hydronephrosis",
        "output": "Right kidney demonstrates mild hydronephrosis. Left kidney appears normal without hydronephrosis or stones. No renal masses or cysts identified bilaterally."
    },
    "reproductive": {
        "template": "Reproductive organs are unremarkable.",
        "finding": "3.2x4.5x9.0 cm right adnexal mass increased from prior previously 2.4 x 2.3 x 2.3 cm (Series 4, Image 76)",
        "output": "There is a right adnexal mass measuring 3.2 x 4.5 x 9.0 cm demonstrating interval growth from prior measurement of 2.4 x 2.3 x 2.3 cm (Series 4, Image 76). Left adnexa appears normal without masses or cysts."
    },
    
    "lymph_nodes": {
        "template": "No abnormally enlarged lymph nodes.",
        "finding": "increased 12 mm aortocaval lymph node previously 7mm",
        "output": "There is an enlarged aortocaval lymph node measuring 12 mm, increased from 7 mm on prior examination."
    },
    
    "bones": {
        "template": "No suspicious osseous lesion. Age-appropriate degenerative changes.",
        "finding": "chronic L1 endplate fracture",
        "output": "There is a chronic L1 endplate fracture. No suspicious osseous lesions. Otherwise age-appropriate degenerative changes."
    }
}

def format_preprocessing_example():
    return f"""
Example Input: "{PREPROCESSING_EXAMPLE['input']}"

Example Output:
{json.dumps(PREPROCESSING_EXAMPLE['output'], indent=2)}

IMPORTANT NOTES:
1. Only include series/image numbers that were explicitly mentioned in the input
2. Expand common abbreviations (e.g., "hydro" → "hydronephrosis")
3. Maintain exact measurements and comparative descriptions
4. Do not add any image references that weren't in the original text
"""

# Helper function to format section processing example
def format_section_example(section):
    example = SECTION_PROCESSING_EXAMPLES.get(section)
    if not example:
        return ""
        
    return f"""
Example for {section}:
Template: "{example['template']}"
Finding: {json.dumps(example['finding'])}
Output: "{example['output']}"

IMPORTANT:
1. Only include series/image numbers that were explicitly provided
2. Expand medical abbreviations into their full forms
3. Do not add any imaginary image references
4. For paired structures (kidneys, lungs, adnexa), always describe both sides
5. When one side is abnormal, explicitly state that the other side is normal
6. Maintain natural language flow while being precise
"""

# Function to expand abbreviations in text
def expand_abbreviations(text):
    words = text.split()
    expanded = []
    for word in words:
        # Check if the word (lowercase) is in our abbreviations dictionary
        lower_word = word.lower()
        if lower_word in RADIOLOGY_ABBREVIATIONS:
            expanded.append(RADIOLOGY_ABBREVIATIONS[lower_word])
        else:
            expanded.append(word)
    return " ".join(expanded)
