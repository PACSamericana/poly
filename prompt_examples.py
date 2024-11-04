import json

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
    
    "reproductive": {
        "template": "Reproductive organs are unremarkable.",
        "finding": {
            "finding": "3.2x4.5x9.0 cm right adnexal mass increased from prior previously 2.4 x 2.3 x 2.3 cm",
            "series": "4",
            "image": "76"
        },
        "output": "There is a right adnexal mass measuring 3.2 x 4.5 x 9.0 cm demonstrating interval growth from prior measurement of 2.4 x 2.3 x 2.3 cm (Series 4, Image 76)."
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

# Helper function to format preprocessing example for prompt
def format_preprocessing_example():
    return f"""
Example Input: "{PREPROCESSING_EXAMPLE['input']}"

Example Output:
{json.dumps(PREPROCESSING_EXAMPLE['output'], indent=2)}
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
"""
