# ============================================================
# UrbanNexus - AI-Assisted Urban Dependency Engine
# ============================================================

import re
from math import radians, sin, cos, sqrt, atan2


# ============================================================
# 1. URBAN CAUSAL KNOWLEDGE BASE
# ============================================================
#
# Format:
#
# upstream problem
#       ↓
# downstream effect
#
# The engine uses these relationships together with
# location + text + category evidence.
# ============================================================

DEPENDENCY_RULES = [

    {
        "source": [
            "blocked drain",
            "blocked drainage",
            "poor drainage",
            "drainage blockage",
            "stormwater blockage",
            "drain blockage"
        ],
        "target": [
            "waterlogging",
            "water logging",
            "flooding",
            "flood",
            "standing water"
        ],
        "relationship": "Drainage blockage may cause waterlogging",
        "strength": 0.95
    },

    {
        "source": [
            "waterlogging",
            "water logging",
            "flooding",
            "flood",
            "standing water"
        ],
        "target": [
            "road blockage",
            "blocked road",
            "road closure",
            "road obstruction"
        ],
        "relationship": "Waterlogging may cause road blockage",
        "strength": 0.88
    },

    {
        "source": [
            "road blockage",
            "blocked road",
            "road closure",
            "road obstruction",
            "damaged road",
            "pothole",
            "potholes"
        ],
        "target": [
            "traffic congestion",
            "traffic jam",
            "congestion",
            "traffic",
            "vehicle delay"
        ],
        "relationship": "Road obstruction may cause traffic congestion",
        "strength": 0.86
    },

    {
        "source": [
            "traffic congestion",
            "traffic jam",
            "congestion",
            "traffic"
        ],
        "target": [
            "travel delay",
            "vehicle delay",
            "emergency delay",
            "ambulance delay",
            "response delay"
        ],
        "relationship": "Traffic congestion may delay vehicle movement",
        "strength": 0.80
    },

    {
        "source": [
            "garbage",
            "waste",
            "trash",
            "dumping",
            "waste accumulation"
        ],
        "target": [
            "pollution",
            "environmental pollution",
            "health risk",
            "public health",
            "bad smell"
        ],
        "relationship": "Poor waste management may create health and environmental risks",
        "strength": 0.82
    },

    {
        "source": [
            "streetlight",
            "street light",
            "lighting failure",
            "light not working",
            "poor lighting"
        ],
        "target": [
            "poor visibility",
            "reduced visibility",
            "night safety",
            "safety risk",
            "dark road"
        ],
        "relationship": "Lighting failure may reduce night-time visibility",
        "strength": 0.84
    },

    {
        "source": [
            "road damage",
            "damaged road",
            "pothole",
            "potholes",
            "broken road"
        ],
        "target": [
            "vehicle damage",
            "traffic congestion",
            "traffic",
            "travel delay",
            "accident risk"
        ],
        "relationship": "Road damage may disrupt vehicle movement",
        "strength": 0.78
    }
]


# ============================================================
# 2. CATEGORY RELATIONSHIPS
# ============================================================

CATEGORY_RELATIONSHIPS = {
    "water & drainage": [
        "waterlogging",
        "flooding",
        "road blockage",
        "traffic"
    ],

    "roads & infrastructure": [
        "traffic",
        "congestion",
        "vehicle delay",
        "accident risk"
    ],

    "traffic": [
        "travel delay",
        "emergency delay",
        "response delay"
    ],

    "waste management": [
        "pollution",
        "health risk",
        "public health"
    ],

    "electricity & lighting": [
        "poor visibility",
        "safety risk"
    ],

    "environment": [
        "pollution",
        "public health"
    ]
}


# ============================================================
# 3. TEXT NORMALIZATION
# ============================================================

def normalize_text(value):
    """
    Convert text into a normalized lowercase string.
    """

    if value is None:
        return ""

    text = str(value).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# 4. GET REPORT TEXT
# ============================================================

def get_report_text(report):
    """
    Combine the important textual fields of a report.
    """

    title = normalize_text(
        report.get("title", "")
    )

    description = normalize_text(
        report.get("description", "")
    )

    category = normalize_text(
        report.get("category", "")
    )

    return " ".join([
        title,
        description,
        category
    ])


# ============================================================
# 5. TOKEN SIMILARITY
# ============================================================

def calculate_text_similarity(text_a, text_b):
    """
    Simple explainable semantic-style similarity.

    Uses meaningful word overlap rather than requiring
    an external AI API.
    """

    words_a = set(
        word
        for word in normalize_text(text_a).split()
        if len(word) > 2
    )

    words_b = set(
        word
        for word in normalize_text(text_b).split()
        if len(word) > 2
    )

    if not words_a or not words_b:
        return 0.0

    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)

    if not union:
        return 0.0

    return len(intersection) / len(union)


# ============================================================
# 6. CAUSAL RELATIONSHIP DETECTION
# ============================================================

def detect_causal_relationship(source_report, target_report):
    """
    Determine whether source_report can contribute to
    target_report using the urban dependency knowledge base.
    """

    source_text = get_report_text(
        source_report
    )

    target_text = get_report_text(
        target_report
    )

    best_match = None

    for rule in DEPENDENCY_RULES:

        source_match = any(
            keyword in source_text
            for keyword in rule["source"]
        )

        if not source_match:
            continue

        target_match = any(
            keyword in target_text
            for keyword in rule["target"]
        )

        if not target_match:
            continue

        if (
            best_match is None
            or rule["strength"] >
               best_match["strength"]
        ):
            best_match = {
                "relationship":
                    rule["relationship"],

                "strength":
                    rule["strength"]
            }

    if best_match:
        return best_match

    return {
        "relationship": None,
        "strength": 0.0
    }


# ============================================================
# 7. CATEGORY RELATIONSHIP
# ============================================================

def calculate_category_relationship(
    source_report,
    target_report
):
    """
    Check whether the categories naturally indicate
    a dependency.
    """

    source_category = normalize_text(
        source_report.get("category", "")
    )

    target_text = get_report_text(
        target_report
    )

    if not source_category:
        return 0.0

    related_terms = CATEGORY_RELATIONSHIPS.get(
        source_category,
        []
    )

    if not related_terms:
        return 0.0

    for term in related_terms:

        if term in target_text:
            return 1.0

    return 0.0


# ============================================================
# 8. DISTANCE CALCULATION
# ============================================================

def calculate_distance_km(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2
):
    """
    Calculate geographical distance between two reports.
    """

    try:

        latitude_1 = float(latitude_1)
        longitude_1 = float(longitude_1)

        latitude_2 = float(latitude_2)
        longitude_2 = float(longitude_2)

    except (
        TypeError,
        ValueError
    ):
        return None

    earth_radius_km = 6371.0

    d_lat = radians(
        latitude_2 - latitude_1
    )

    d_lon = radians(
        longitude_2 - longitude_1
    )

    a = (
        sin(d_lat / 2) ** 2
        +
        cos(radians(latitude_1))
        *
        cos(radians(latitude_2))
        *
        sin(d_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius_km * c


# ============================================================
# 9. LOCATION PROXIMITY SCORE
# ============================================================

def calculate_location_score(
    source_report,
    target_report
):
    """
    Convert geographical distance into a relationship score.

    <= 0.5 km  → very strong
    <= 1 km    → strong
    <= 2 km    → moderate
    <= 5 km    → weak
    > 5 km     → very weak
    """

    distance = calculate_distance_km(
        source_report.get("latitude"),
        source_report.get("longitude"),
        target_report.get("latitude"),
        target_report.get("longitude")
    )

    if distance is None:
        return {
            "distance_km": None,
            "score": 0.0
        }

    if distance <= 0.5:
        score = 1.0

    elif distance <= 1:
        score = 0.85

    elif distance <= 2:
        score = 0.65

    elif distance <= 5:
        score = 0.35

    else:
        score = 0.10

    return {
        "distance_km": round(
            distance,
            3
        ),
        "score": score
    }


# ============================================================
# 10. DEPENDENCY STRENGTH
# ============================================================

def calculate_dependency_strength(
    causal_score,
    text_score,
    location_score,
    category_score
):
    """
    Weighted dependency score.

    Causal relationship  = 40%
    Text relationship    = 25%
    Location proximity   = 25%
    Category relation    = 10%
    """

    score = (
        causal_score * 0.40
        +
        text_score * 0.25
        +
        location_score * 0.25
        +
        category_score * 0.10
    )

    return round(
        score * 100,
        1
    )


# ============================================================
# 11. RELATIONSHIP LABEL
# ============================================================

def get_dependency_level(score):

    if score >= 80:
        return "STRONG"

    if score >= 60:
        return "MODERATE"

    if score >= 40:
        return "WEAK"

    return "LOW"


# ============================================================
# 12. CASCADING EFFECTS
# ============================================================

def get_cascading_effects(report):
    """
    Determine likely downstream effects from the report.
    """

    report_text = get_report_text(
        report
    )

    effects = []

    for rule in DEPENDENCY_RULES:

        source_match = any(
            keyword in report_text
            for keyword in rule["source"]
        )

        if source_match:

            for keyword in rule["target"]:

                readable_name = (
                    keyword
                    .replace(
                        "water logging",
                        "Waterlogging"
                    )
                    .replace(
                        "traffic congestion",
                        "Traffic Congestion"
                    )
                    .replace(
                        "road blockage",
                        "Road Blockage"
                    )
                    .replace(
                        "emergency delay",
                        "Emergency Response Delay"
                    )
                )

                readable_name = (
                    readable_name
                    .title()
                )

                if readable_name not in effects:
                    effects.append(
                        readable_name
                    )

    return effects[:6]


# ============================================================
# 13. DEPENDENCY ANALYSIS
# ============================================================

def analyze_dependencies(
    report,
    all_reports,
    minimum_score=40
):
    """
    Analyze one urban problem against all other
    urban problems.

    Returns:

    {
        dependency_score,
        dependencies,
        root_cause,
        cascading_effects,
        dependency_analyzed
    }
    """

    dependencies = []

    report_id = str(
        report.get("_id", "")
    )

    current_text = get_report_text(
        report
    )

    best_upstream = None

    for other_report in all_reports:

        other_id = str(
            other_report.get("_id", "")
        )

        # Do not compare the report with itself.
        if other_id == report_id:
            continue

        other_text = get_report_text(
            other_report
        )

        # ----------------------------------------
        # TEXT RELATIONSHIP
        # ----------------------------------------

        text_score = calculate_text_similarity(
            current_text,
            other_text
        )

        # ----------------------------------------
        # CAUSAL RELATIONSHIP
        # ----------------------------------------

        forward_causal = detect_causal_relationship(
            other_report,
            report
        )

        reverse_causal = detect_causal_relationship(
            report,
            other_report
        )

        # We need to know which direction is stronger.
        if (
            forward_causal["strength"]
            >=
            reverse_causal["strength"]
        ):

            causal = forward_causal

            source_report = other_report
            target_report = report

            direction = "UPSTREAM"

        else:

            causal = reverse_causal

            source_report = report
            target_report = other_report

            direction = "DOWNSTREAM"

        # ----------------------------------------
        # LOCATION
        # ----------------------------------------

        location = calculate_location_score(
            report,
            other_report
        )

        location_score = location["score"]

        # ----------------------------------------
        # CATEGORY
        # ----------------------------------------

        category_score = calculate_category_relationship(
            source_report,
            target_report
        )

        # ----------------------------------------
        # FINAL DEPENDENCY SCORE
        # ----------------------------------------

        dependency_score = calculate_dependency_strength(
            causal["strength"],
            text_score,
            location_score,
            category_score
        )

        # ----------------------------------------
        # FILTER LOW RELATIONSHIPS
        # ----------------------------------------

        if dependency_score < minimum_score:
            continue

        dependency_level = get_dependency_level(
            dependency_score
        )

        dependency = {
            "problem_id": other_id,

            "title": other_report.get(
                "title",
                "Urban Problem"
            ),

            "category": other_report.get(
                "category",
                "General"
            ),

            "relationship": (
                causal["relationship"]
                or
                "Potential related urban problem"
            ),

            "direction": direction,

            "strength": round(
                dependency_score / 100,
                3
            ),

            "score": dependency_score,

            "level": dependency_level,

            "distance_km":
                location["distance_km"],

            "signals": {
                "causal": round(
                    causal["strength"] * 100,
                    1
                ),

                "text_similarity": round(
                    text_score * 100,
                    1
                ),

                "location_proximity": round(
                    location_score * 100,
                    1
                ),

                "category_relationship": round(
                    category_score * 100,
                    1
                )
            }
        }

        dependencies.append(
            dependency
        )

        # ----------------------------------------
        # ROOT CAUSE CANDIDATE
        # ----------------------------------------

        if (
            direction == "UPSTREAM"
            and causal["strength"] > 0
        ):

            if (
                best_upstream is None
                or
                dependency_score
                >
                best_upstream["score"]
            ):

                best_upstream = dependency

    # ========================================================
    # SORT DEPENDENCIES
    # ========================================================

    dependencies.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    dependencies = dependencies[:10]

    # ========================================================
    # ROOT CAUSE
    # ========================================================

    existing_root_cause = report.get(
        "root_cause"
    )

    if best_upstream:

        root_cause = (
            best_upstream["title"]
        )

        root_cause_type = "RELATED_UPSTREAM_PROBLEM"

    elif (
        existing_root_cause
        and
        existing_root_cause !=
        "Local infrastructure issue"
    ):

        root_cause = existing_root_cause

        root_cause_type = "REPORT_ANALYSIS"

    else:

        root_cause = (
            "No strong upstream cause identified"
        )

        root_cause_type = "UNDETERMINED"

    # ========================================================
    # CASCADING EFFECTS
    # ========================================================

    cascading_effects = get_cascading_effects(
        report
    )

    # Add downstream dependency titles.
    for dependency in dependencies:

        if (
            dependency["direction"]
            == "DOWNSTREAM"
        ):

            title = dependency["title"]

            if title not in cascading_effects:

                cascading_effects.append(
                    title
                )

    cascading_effects = cascading_effects[:6]

    # ========================================================
    # OVERALL DEPENDENCY SCORE
    # ========================================================

    if dependencies:

        overall_score = max(
            dependency["score"]
            for dependency in dependencies
        )

    else:

        overall_score = 0

    return {

        "dependency_score":
            round(
                overall_score,
                1
            ),

        "dependencies":
            dependencies,

        "root_cause":
            root_cause,

        "root_cause_type":
            root_cause_type,

        "cascading_effects":
            cascading_effects,

        "dependency_analyzed":
            True
    }