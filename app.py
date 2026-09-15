from flask import Flask, render_template
from dependency_engine import analyze_dependencies
from flask import Flask, render_template, request, redirect, url_for
from database import db
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
from flask import Flask, render_template, request, redirect, url_for, session
from database import db
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests

app.secret_key = "urbannexus-secret-key-2026"

# ============================================================
# MIGRATE OLD DEMO REPORTS
# ============================================================

db.problems.update_many(
    {
        "citizen_id": {
            "$exists": False
        }
    },
    {
        "$set": {
            "citizen_id": "demo_citizen"
        }
    }
)


# ============================================================
# URBANNEXUS AI ANALYSIS ENGINE
# ============================================================

def analyze_urban_problem(title, description, category):
    """
    Analyze a citizen-reported urban problem.

    Returns:
        impact_level
        priority
        root_cause
        connected_problems
        cascading_effects
        ai_explanation
    """

    title_text = (title or "").lower()
    description_text = (description or "").lower()
    category_text = (category or "").lower()

    text = " ".join([
        title_text,
        description_text,
        category_text
    ])


    # --------------------------------------------------------
    # DEFAULT VALUES
    # --------------------------------------------------------

    impact_level = "MEDIUM"
    priority = "MEDIUM"

    root_cause = "Local infrastructure issue"

    connected_problems = 0

    cascading_effects = []

    ai_explanation = (
        "UrbanNexus identified this as an urban infrastructure "
        "problem requiring municipal attention."
    )


    # ========================================================
    # WATER & DRAINAGE
    # ========================================================

    if (
        "water" in text
        or "drain" in text
        or "drainage" in text
        or "waterlogging" in text
        or "flood" in text
        or "flooding" in text
    ):

        root_cause = "Poor drainage or blocked stormwater infrastructure"

        connected_problems = 3

        cascading_effects = [
            "Waterlogging",
            "Road Blockage",
            "Traffic Congestion"
        ]

        impact_level = "HIGH"
        priority = "HIGH"

        ai_explanation = (
            "UrbanNexus identified a potential drainage-related "
            "dependency. A blocked or inadequate drainage system "
            "can cause waterlogging, road blockage and downstream "
            "traffic congestion."
        )


    # ========================================================
    # ROADS
    # ========================================================

    elif (
        "road" in text
        or "pothole" in text
        or "potholes" in text
        or "damaged road" in text
        or "road damage" in text
    ):

        root_cause = "Damaged or poorly maintained road infrastructure"

        connected_problems = 2

        cascading_effects = [
            "Traffic Congestion",
            "Vehicle Movement Delay"
        ]

        impact_level = "MEDIUM"
        priority = "MEDIUM"

        ai_explanation = (
            "UrbanNexus identified a road infrastructure problem "
            "that may affect traffic flow and vehicle movement."
        )


    # ========================================================
    # TRAFFIC
    # ========================================================

    elif (
        "traffic" in text
        or "congestion" in text
        or "signal" in text
        or "junction" in text
        or "jam" in text
    ):

        root_cause = "Traffic flow disruption or inadequate traffic management"

        connected_problems = 2

        cascading_effects = [
            "Travel Delay",
            "Emergency Response Delay"
        ]

        impact_level = "HIGH"
        priority = "HIGH"

        ai_explanation = (
            "UrbanNexus identified a traffic-related issue that "
            "may create wider delays and affect emergency vehicle "
            "movement."
        )


    # ========================================================
    # WASTE MANAGEMENT
    # ========================================================

    elif (
        "garbage" in text
        or "waste" in text
        or "dumping" in text
        or "trash" in text
    ):

        root_cause = "Improper waste collection or waste disposal"

        connected_problems = 2

        cascading_effects = [
            "Public Health Risk",
            "Environmental Pollution"
        ]

        impact_level = "MEDIUM"
        priority = "MEDIUM"

        ai_explanation = (
            "UrbanNexus identified a waste-management problem "
            "that may create environmental and public health impacts."
        )


    # ========================================================
    # ELECTRICITY & LIGHTING
    # ========================================================

    elif (
        "streetlight" in text
        or "street light" in text
        or "electricity" in text
        or "lighting" in text
        or "light not working" in text
    ):

        root_cause = "Faulty electrical or street-lighting infrastructure"

        connected_problems = 1

        cascading_effects = [
            "Reduced Night-time Visibility"
        ]

        impact_level = "LOW"
        priority = "LOW"

        ai_explanation = (
            "UrbanNexus identified a local lighting issue that "
            "primarily affects visibility and public safety."
        )


    # ========================================================
    # PARKS & ENVIRONMENT
    # ========================================================

    elif (
        "park" in text
        or "environment" in text
        or "tree" in text
        or "pollution" in text
        or "public space" in text
    ):

        root_cause = "Environmental or public-space maintenance issue"

        connected_problems = 1

        cascading_effects = [
            "Environmental Quality Reduction"
        ]

        impact_level = "LOW"
        priority = "LOW"

        ai_explanation = (
            "UrbanNexus identified an environmental or public-space "
            "issue requiring local maintenance."
        )


    # ========================================================
    # SEVERE IMPACT KEYWORDS
    # ========================================================

    severe_keywords = [
        "accident",
        "dangerous",
        "emergency",
        "hospital",
        "ambulance",
        "flood",
        "flooding",
        "major blockage",
        "severe",
        "critical",
        "life threatening"
    ]

    severe_match = any(
        keyword in text
        for keyword in severe_keywords
    )


    if severe_match:

        impact_level = "HIGH"
        priority = "HIGH"


    # ========================================================
    # RETURN AI RESULT
    # ========================================================

    return {
        "impact_level": impact_level,
        "priority": priority,
        "root_cause": root_cause,
        "connected_problems": connected_problems,
        "cascading_effects": cascading_effects,
        "ai_explanation": ai_explanation,
        "ai_analyzed": True,
        "ai_analyzed_at": datetime.utcnow()
    }

# ============================================================
# TEMPORARY: ANALYZE OLD REPORTS
# ============================================================

@app.route("/admin/analyze-old-reports")
def analyze_old_reports():

    # Find reports that have NOT been analyzed by AI yet
    old_reports = list(
        db.problems.find({
            "$or": [
                {"ai_analyzed": {"$exists": False}},
                {"ai_analyzed": False}
            ]
        })
    )

    analyzed_count = 0

    for report in old_reports:

        title = report.get(
            "title",
            ""
        )

        description = report.get(
            "description",
            ""
        )

        category = report.get(
            "category",
            ""
        )


        # Run the existing AI analysis engine
        ai_result = analyze_urban_problem(
            title,
            description,
            category
        )


        # Update the EXISTING MongoDB document
        db.problems.update_one(
            {
                "_id": report["_id"]
            },
            {
                "$set": {
                    **ai_result,
                    "status": "AI Analyzed"
                }
            }
        )

        analyzed_count += 1


    print("==========================================")
    print("OLD REPORT AI MIGRATION")
    print("==========================================")
    print("REPORTS FOUND:", len(old_reports))
    print("REPORTS ANALYZED:", analyzed_count)
    print("==========================================")


    return (
        f"AI analysis completed successfully.<br><br>"
        f"Reports found: {len(old_reports)}<br>"
        f"Reports analyzed: {analyzed_count}<br><br>"
        f"You can now return to the Citizen Dashboard."
    )
# =========================
# CITIZEN DASHBOARD
# =========================

@app.route("/")
def home():
    return redirect(
        url_for("citizen_dashboard")
    )


@app.route("/citizen/dashboard")
def citizen_dashboard():

    # ============================================================
    # CURRENT CITIZEN
    # ============================================================
    # For now we use a demo citizen.
    # Later this will come from the login system.

    citizen_id = session.get(
        "citizen_id",
        "demo_citizen"
    )

    # Keep citizen ID in the session
    session["citizen_id"] = citizen_id


    # ============================================================
    # GET THIS CITIZEN'S REPORTS FROM MONGODB
    # ============================================================

    reports = list(
        db.problems.find({
            "citizen_id": citizen_id
        }).sort("_id", -1)
    )


    # ============================================================
    # NORMALIZE REPORT DATA
    # ============================================================
    # This makes sure old reports without some fields
    # don't break the dashboard.

    for report in reports:

        if not report.get("status"):
            report["status"] = "Submitted"

        if not report.get("impact_level"):
            report["impact_level"] = "MEDIUM"

        if not report.get("priority"):
            report["priority"] = report.get(
                "impact_level",
                "MEDIUM"
            )

        if not report.get("category"):
            report["category"] = "General"

        if not report.get("address"):
            report["address"] = report.get(
                "location",
                "Location not provided"
            )


    # ============================================================
    # TOTAL REPORTS
    # ============================================================

    total_reports = len(reports)


    # ============================================================
    # ACTIVE REPORTS
    # ============================================================
    # Reports that have already moved beyond submission
    # and are currently being handled.

    active_reports = sum(
        1
        for report in reports
        if report.get("status") in [
             "Submitted",
        "AI Analyzed",
        "Verified",
        "Assigned",
        "In Progress"
        ]
    )


    # ============================================================
    # REPORTS WITH AI ANALYSIS
    # ============================================================
    # Your AI engine currently produces AI results during
    # submission. Therefore we detect AI-analyzed reports
    # using the stored AI fields as well as the status.

    analysis_reports = sum(
        1
        for report in reports
        if (
            report.get("status") == "AI Analyzed"
            or (
                report.get("impact_level")
                and report.get("root_cause")
                and report.get("connected_problems") is not None
            )
        )
    )


    # ============================================================
    # RESOLVED REPORTS
    # ============================================================

    resolved_reports = sum(
        1
        for report in reports
        if report.get("status") == "Resolved"
    )


    # ============================================================
    # RECENT REPORTS
    # ============================================================
    # Only the latest 5 reports are shown in the dashboard.

    recent_reports = reports[:5]


    # ============================================================
    # CITY PROBLEMS
    # ============================================================
    # These are the latest problems reported in UrbanNexus.
    #
    # Later this can be changed to true nearby problems using
    # latitude + longitude / geospatial search.

    city_problems = list(
        db.problems.find({}).sort("_id", -1).limit(3)
    )


    # ============================================================
    # NORMALIZE CITY PROBLEMS
    # ============================================================

    for problem in city_problems:

        if not problem.get("title"):
            problem["title"] = "Urban Problem"

        if not problem.get("category"):
            problem["category"] = "General"

        if not problem.get("address"):
            problem["address"] = problem.get(
                "location",
                "Location not provided"
            )

        if not problem.get("impact_level"):
            problem["impact_level"] = "MEDIUM"


    # ============================================================
    # DEBUG INFORMATION
    # ============================================================

    print("==========================================")
    print("CITIZEN DASHBOARD")
    print("==========================================")
    print("CITIZEN ID:", citizen_id)
    print("TOTAL REPORTS:", total_reports)
    print("ACTIVE REPORTS:", active_reports)
    print("AI ANALYZED:", analysis_reports)
    print("RESOLVED:", resolved_reports)
    print("RECENT REPORTS:", len(recent_reports))
    print("CITY PROBLEMS:", len(city_problems))
    print("==========================================")


    # ============================================================
    # SEND DATA TO DASHBOARD
    # ============================================================

    return render_template(
        "citizen/dashboard.html",

        # Complete reports
        reports=reports,

        # Latest 5 reports
        recent_reports=recent_reports,

        # Latest city problems
        city_problems=city_problems,

        # Dashboard statistics
        total_reports=total_reports,
        active_reports=active_reports,
        analysis_reports=analysis_reports,
        resolved_reports=resolved_reports,

        # Sidebar active item
        active_page="dashboard"
    )
@app.route("/citizen/report", methods=["GET", "POST"])
def report_problem():

    if request.method == "POST":

        # ====================================================
        # CITIZEN ID
        # ====================================================
        # Temporary citizen ID until login/authentication
        # is implemented.
        # ====================================================

        citizen_id = session.get(
            "citizen_id",
            "demo_citizen"
        )

        session["citizen_id"] = citizen_id


        # ====================================================
        # GET FORM DATA
        # ====================================================

        categories = request.form.getlist("categories")

        category = ", ".join(categories)

        print(
            "CATEGORIES RECEIVED:",
            categories
        )


        title = request.form.get(
            "title",
            "Untitled Problem"
        )

        description = request.form.get(
            "description",
            ""
        )

        address = request.form.get(
            "address",
            "Location not provided"
        )
        latitude = request.form.get(
    "latitude"
)

        longitude = request.form.get(
    "longitude"
)

        # ====================================================
        # BASIC REPORT DATA
        # ====================================================

        report = {

            # Citizen who submitted the report
            "citizen_id": citizen_id,

            # Problem information
            "category": category,

            "title": title,

            "description": description,

            "address": address,

            # Keep location for Report Details
            "location": address,
            "latitude": (
        float(latitude)
        if latitude
        else None
    ),

    "longitude": (
        float(longitude)
        if longitude
        else None
    ),
            # Initial status
            "status": "Submitted",

            # Initial values
            "impact_level": "MEDIUM",

            "priority": "MEDIUM",

            "department": "Awaiting Assignment",

            # Initial progress
            "progress": 25,

            # Creation time
            "created_at": datetime.utcnow()
        }


        # ====================================================
        # URBANNEXUS AI ANALYSIS
        # ====================================================

        ai_result = analyze_urban_problem(
            title,
            description,
            category
        )


        # ====================================================
        # ADD AI RESULTS
        # ====================================================

        if ai_result:

            report.update(ai_result)
            report["status"] = "AI Analyzed"


        # ====================================================
        # PRINT WHAT IS BEING SAVED
        # ====================================================

        print("==========================================")
        print("SAVING REPORT:")
        print("CITIZEN ID:", report.get("citizen_id"))
        print("TITLE:", report.get("title"))
        print("CATEGORY:", report.get("category"))
        print("IMPACT:", report.get("impact_level"))
        print("PRIORITY:", report.get("priority"))
        print("ROOT CAUSE:", report.get("root_cause"))
        print(
            "CONNECTED PROBLEMS:",
            report.get("connected_problems")
        )
        print(
            "CASCADING EFFECTS:",
            report.get("cascading_effects")
        )
        print("==========================================")


        # ====================================================
        # SAVE TO MONGODB
        # ====================================================

        result = db.problems.insert_one(report)

        print(
    "LOCATION SAVED:",
    report.get("latitude"),
    report.get("longitude")
)
        print(
            "REPORT SAVED WITH ID:",
            result.inserted_id
        )


        # ====================================================
        # REDIRECT TO MY REPORTS
        # ====================================================

        return redirect(
            url_for("my_reports")
        )


    # ========================================================
    # SHOW REPORT FORM
    # ========================================================

    return render_template(
        "citizen/report_problem.html",
        active_page="report"
    )


@app.route("/citizen/reports")
def my_reports():

    # ============================================================
    # CURRENT CITIZEN
    # ============================================================

    citizen_id = session.get(
        "citizen_id",
        "demo_citizen"
    )

    session["citizen_id"] = citizen_id


    # ============================================================
    # GET ONLY THIS CITIZEN'S REPORTS
    # ============================================================

    reports = list(
        db.problems.find({
            "citizen_id": citizen_id
        }).sort("_id", -1)
    )


    # ============================================================
    # NORMALIZE REPORT DATA
    # ============================================================

    for report in reports:

        if not report.get("title"):
            report["title"] = "Untitled Problem"

        if not report.get("category"):
            report["category"] = "General"

        if not report.get("status"):
            report["status"] = "Submitted"

        if not report.get("impact_level"):
            report["impact_level"] = "MEDIUM"

        if not report.get("priority"):
            report["priority"] = report.get(
                "impact_level",
                "MEDIUM"
            )

        if not report.get("address"):
            report["address"] = report.get(
                "location",
                "Location not provided"
            )


    # ============================================================
    # STATISTICS
    # ============================================================

    total_reports = len(reports)


    active_reports = sum(
        1
        for report in reports
        if report.get("status") in [
            "Submitted",
            "AI Analyzed",
            "Verified",
            "Assigned",
            "In Progress"
        ]
    )


    analysis_reports = sum(
        1
        for report in reports
        if (
            report.get("status") == "AI Analyzed"
            or (
                report.get("impact_level")
                and report.get("root_cause")
                and report.get("connected_problems") is not None
            )
        )
    )


    resolved_reports = sum(
        1
        for report in reports
        if report.get("status") == "Resolved"
    )


    # ============================================================
    # DEBUG
    # ============================================================

    print("==========================================")
    print("MY REPORTS")
    print("==========================================")
    print("CITIZEN ID:", citizen_id)
    print("TOTAL REPORTS:", total_reports)
    print("ACTIVE REPORTS:", active_reports)
    print("AI ANALYZED:", analysis_reports)
    print("RESOLVED:", resolved_reports)

    for report in reports:

        print(
            "ID:",
            report.get("_id"),
            "| TITLE:",
            report.get("title"),
            "| STATUS:",
            report.get("status")
        )

    print("==========================================")


    # ============================================================
    # SEND DATA TO TEMPLATE
    # ============================================================

    return render_template(
        "citizen/my_reports.html",

        reports=reports,

        total_reports=total_reports,
        active_reports=active_reports,
        analysis_reports=analysis_reports,
        resolved_reports=resolved_reports,

        active_page="reports"
    )   

@app.route("/citizen/report/<report_id>")
def report_details(report_id):

    from bson.objectid import ObjectId
    from bson.errors import InvalidId

    # =====================================================
    # CHECK REPORT ID
    # =====================================================

    try:

        object_id = ObjectId(report_id)

    except InvalidId:

        return "Invalid report ID", 400


    # =====================================================
    # GET CURRENT CITIZEN
    # =====================================================

    citizen_id = session.get(
        "citizen_id",
        "demo_citizen"
    )

    session["citizen_id"] = citizen_id


    # =====================================================
    # GET ONLY THIS CITIZEN'S REPORT
    #
    # IMPORTANT:
    # citizen_id prevents one citizen from opening
    # another citizen's private report.
    # =====================================================

    report = db.problems.find_one({

        "_id": object_id,

        "citizen_id": citizen_id

    })


    # =====================================================
    # REPORT NOT FOUND
    # =====================================================

    if not report:

        return "Report not found", 404


    # =====================================================
    # PREPARE VALUES
    # =====================================================

    title = report.get(
        "title",
        "Untitled Problem"
    )


    category = report.get(
        "category",
        "General"
    )


    location = report.get(
        "address",
        report.get(
            "location",
            "Location not provided"
        )
    )


    description = report.get(
        "description",
        ""
    )


    # =====================================================
    # IMPACT
    # =====================================================

    impact_level = report.get(
        "impact_level",
        report.get(
            "impact",
            "MEDIUM"
        )
    )


    # =====================================================
    # PRIORITY
    # =====================================================

    priority = report.get(
        "priority",
        impact_level
    )


    # =====================================================
    # STATUS
    # =====================================================

    status = report.get(
        "status",
        "Submitted"
    )


    # =====================================================
    # PROGRESS
    # =====================================================

    progress = report.get(
        "progress",
        25
    )


    # =====================================================
    # CONNECTED PROBLEMS
    # =====================================================

    connected_problems = report.get(
        "connected_problems",
        0
    )


    # =====================================================
    # DEPARTMENT
    # =====================================================

    department = report.get(
        "department",
        "Awaiting Assignment"
    )


    # =====================================================
    # CREATED DATE
    # =====================================================

    created_at = report.get(
        "created_at"
    )


    if created_at:

        try:

            reported_date = created_at.strftime(
                "%d %b %Y"
            )

        except AttributeError:

            reported_date = str(
                created_at
            )

    else:

        reported_date = "Just submitted"


    # =====================================================
    # RETURN CITIZEN PRIVATE REPORT PAGE
    # =====================================================

    return render_template(

        "citizen/report_details.html",

        report=report,

        title=title,

        category=category,

        location=location,

        description=description,

        impact_level=str(
            impact_level
        ).upper(),

        priority=str(
            priority
        ).upper(),

        status=status,

        progress=progress,

        department=department,

        reported_date=reported_date,

        connected_problems=connected_problems,

        active_page="reports"

    )
@app.route("/citizen/nearby")
def nearby_problems():
    return render_template(
        "citizen/nearby_problems.html",
        active_page="nearby"
    )

@app.route("/citizen/notifications")
def notifications():
    return render_template(
        "citizen/notifications.html",
        active_page="notifications"
    )

@app.route("/citizen/profile")
def profile():
    return render_template(
        "citizen/profile.html",
        active_page="profile"
    )

@app.route("/municipality/dashboard")
def municipality_dashboard():
    return render_template(
        "municipality/dashboard.html",
        active_page="municipality-dashboard",
        portal="municipality"
    )


@app.route("/reanalyze-all")
def reanalyze_all():

    # Get every report from MongoDB
    reports = list(
        db.problems.find({})
    )

    analyzed_count = 0

    for report in reports:

        title = report.get("title", "")
        description = report.get("description", "")

        category = report.get("category")


        # ====================================================
        # FIX MISSING CATEGORY
        # ====================================================

        if not category:

            text = (
                str(title) + " " +
                str(description)
            ).lower()


            if (
                "water" in text
                or "drain" in text
                or "drainage" in text
                or "waterlogging" in text
                or "flood" in text
            ):

                category = "Water & Drainage"


            elif (
                "road" in text
                or "pothole" in text
                or "potholes" in text
            ):

                category = "Roads & Infrastructure"


            elif (
                "traffic" in text
                or "congestion" in text
                or "signal" in text
                or "junction" in text
            ):

                category = "Traffic"


            elif (
                "garbage" in text
                or "waste" in text
                or "dumping" in text
                or "trash" in text
            ):

                category = "Waste Management"


            elif (
                "streetlight" in text
                or "street light" in text
                or "electricity" in text
                or "lighting" in text
            ):

                category = "Electricity & Lighting"


            else:

                category = "General"


        # ====================================================
        # RUN YOUR EXISTING AI FUNCTION
        # ====================================================

        ai_result = analyze_urban_problem(
            title,
            description,
            category
        )


        # ====================================================
        # UPDATE THE SAME MONGODB DOCUMENT
        # ====================================================

        db.problems.update_one(

            {
                "_id": report["_id"]
            },

            {
                "$set": {

                    "category":
                        category,

                    "impact_level":
                        ai_result["impact_level"],

                    "priority":
                        ai_result["priority"],

                    "root_cause":
                        ai_result["root_cause"],

                    "connected_problems":
                        ai_result["connected_problems"],

                    "cascading_effects":
                        ai_result["cascading_effects"],

                    "ai_explanation":
                        ai_result["ai_explanation"],

                    "ai_analyzed":
                        True,

                    "ai_analyzed_at":
                        ai_result["ai_analyzed_at"],

                    "status":
                        "AI Analyzed"

                }
            }
        )


        analyzed_count += 1


    return f"""
    <h2>AI analysis completed successfully.</h2>

    <p>Reports found: {len(reports)}</p>

    <p>Reports analyzed: {analyzed_count}</p>

    <p>Missing categories were also fixed.</p>

    <p>
        All reports are now synchronized with the AI analysis.
    </p>
    """
# ============================================================
# MUNICIPAL OFFICER - PROBLEM INTELLIGENCE
# ============================================================
@app.route("/municipality/intelligence")
def municipality_intelligence():

    # ========================================================
    # GET ALL CITIZEN REPORTS FROM MONGODB
    # ========================================================

    reports = list(
        db.problems.find({}).sort("_id", -1)
    )


    # ========================================================
    # PREPARE REPORTS FOR MUNICIPAL INTELLIGENCE
    # ========================================================

    intelligence_reports = []


    for report in reports:

        # ----------------------------------------------------
        # BASIC REPORT INFORMATION
        # ----------------------------------------------------

        report_id = str(
            report.get("_id")
        )

        title = report.get(
            "title",
            "Untitled Problem"
        )

        category = report.get(
            "category",
            "General"
        )

        description = report.get(
            "description",
            ""
        )

        address = report.get(
            "address",
            report.get(
                "location",
                "Location not provided"
            )
        )


        # ----------------------------------------------------
        # CITIZEN INFORMATION
        # ----------------------------------------------------
        # Keep this internally available if needed.
        # Do NOT expose this in the public dependency UI.

        citizen_id = report.get(
            "citizen_id",
            "Unknown Citizen"
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = report.get(
            "status",
            "Submitted"
        )


        # ----------------------------------------------------
        # AI IMPACT
        # ----------------------------------------------------

        impact = report.get(
            "impact_level",
            report.get(
                "impact",
                "MEDIUM"
            )
        )


        # ----------------------------------------------------
        # AI PRIORITY
        # ----------------------------------------------------

        priority = report.get(
            "priority",
            impact
        )


        # ====================================================
        # EXISTING AI ROOT CAUSE
        # ====================================================

        root_cause = report.get(
            "root_cause",
            "Analysis pending"
        )


        # ====================================================
        # NEW DEPENDENCY ENGINE DATA
        # ====================================================

        dependencies = report.get(
            "dependencies",
            []
        )

        # Make sure dependencies is always a list.
        if not isinstance(
            dependencies,
            list
        ):
            dependencies = []


        # ----------------------------------------------------
        # DEPENDENCY SCORE
        # ----------------------------------------------------

        dependency_score = report.get(
            "dependency_score",
            0
        )

        try:

            dependency_score = float(
                dependency_score
            )

        except (
            TypeError,
            ValueError
        ):

            dependency_score = 0


        # ----------------------------------------------------
        # DEPENDENCY ANALYZED
        # ----------------------------------------------------

        dependency_analyzed = report.get(
            "dependency_analyzed",
            False
        )


        # ----------------------------------------------------
        # ROOT CAUSE TYPE
        # ----------------------------------------------------

        root_cause_type = report.get(
            "root_cause_type",
            "UNDETERMINED"
        )


        # ====================================================
        # CONNECTED PROBLEMS
        # ====================================================
        #
        # OLD SYSTEM:
        # connected_problems was manually stored.
        #
        # NEW SYSTEM:
        # calculate it from the actual dependency list.
        # ====================================================

        if dependencies:

            connected_problems = len(
                dependencies
            )

        else:

            connected_problems = report.get(
                "connected_problems",
                0
            )

            try:

                connected_problems = int(
                    connected_problems
                )

            except (
                TypeError,
                ValueError
            ):

                connected_problems = 0


        # ====================================================
        # CASCADING EFFECTS
        # ====================================================

        cascading_effects = report.get(
            "cascading_effects",
            []
        )

        if not isinstance(
            cascading_effects,
            list
        ):
            cascading_effects = []


        # ====================================================
        # AI EXPLANATION
        # ====================================================

        ai_explanation = report.get(
            "ai_explanation",
            "AI analysis not available."
        )


        # ====================================================
        # EXISTING AI ANALYZED FLAG
        # ====================================================

        ai_analyzed = report.get(
            "ai_analyzed",
            False
        )


        # ====================================================
        # CREATED DATE
        # ====================================================

        created_at = report.get(
            "created_at"
        )

        if created_at:

            try:

                reported_date = created_at.strftime(
                    "%d %b %Y"
                )

            except AttributeError:

                reported_date = str(
                    created_at
                )

        else:

            reported_date = "Recently reported"


        # ====================================================
        # ADD PREPARED REPORT
        # ====================================================

        intelligence_reports.append({

            # ----------------------------------------------
            # IDENTIFICATION
            # ----------------------------------------------

            "id": report_id,

            "title": title,

            "category": category,

            "description": description,

            "address": address,


            # ----------------------------------------------
            # CITIZEN
            # ----------------------------------------------

            "citizen_id": citizen_id,


            # ----------------------------------------------
            # STATUS
            # ----------------------------------------------

            "status": status,


            # ----------------------------------------------
            # AI IMPACT
            # ----------------------------------------------

            "impact": str(
                impact
            ).upper(),


            # ----------------------------------------------
            # AI PRIORITY
            # ----------------------------------------------

            "priority": str(
                priority
            ).upper(),


            # ----------------------------------------------
            # ROOT CAUSE
            # ----------------------------------------------

            "root_cause": root_cause,

            "root_cause_type": root_cause_type,


            # ----------------------------------------------
            # DEPENDENCY ENGINE
            # ----------------------------------------------

            "dependency_score":
                dependency_score,

            "dependencies":
                dependencies,

            "dependency_analyzed":
                dependency_analyzed,


            # ----------------------------------------------
            # CONNECTED PROBLEMS
            # ----------------------------------------------

            "connected_problems":
                connected_problems,


            # ----------------------------------------------
            # CASCADING EFFECTS
            # ----------------------------------------------

            "cascading_effects":
                cascading_effects,


            # ----------------------------------------------
            # AI EXPLANATION
            # ----------------------------------------------

            "ai_explanation":
                ai_explanation,

            "ai_analyzed":
                ai_analyzed,


            # ----------------------------------------------
            # DATE
            # ----------------------------------------------

            "reported_date":
                reported_date

        })


    # ========================================================
    # MUNICIPAL INTELLIGENCE STATISTICS
    # ========================================================

    total_problems = len(
        intelligence_reports
    )


    # ========================================================
    # HIGH IMPACT PROBLEMS
    # ========================================================

    high_impact = sum(

        1

        for report in intelligence_reports

        if report["impact"] == "HIGH"

    )


    # ========================================================
    # AI ANALYZED PROBLEMS
    # ========================================================

    analyzed = sum(

        1

        for report in intelligence_reports

        if (
            report["ai_analyzed"] is True

            or

            report["dependency_analyzed"] is True

            or

            report["root_cause"]
            != "Analysis pending"
        )

    )


    # ========================================================
    # CASCADING PROBLEMS
    # ========================================================

    cascading = sum(

        1

        for report in intelligence_reports

        if len(
            report["cascading_effects"]
        ) > 0

    )


    # ========================================================
    # HIGH PRIORITY PROBLEMS
    # ========================================================

    high_priority = sum(

        1

        for report in intelligence_reports

        if report["priority"] == "HIGH"

    )


    # ========================================================
    # UNASSIGNED PROBLEMS
    # ========================================================

    unassigned = sum(

        1

        for report in intelligence_reports

        if report["status"] in [

            "Submitted",

            "AI Analyzed",

            "Verified"

        ]

    )


    # ========================================================
    # DEPENDENCY STATISTICS
    # ========================================================

    dependency_analyzed_count = sum(

        1

        for report in intelligence_reports

        if report["dependency_analyzed"] is True

    )


    strong_dependencies = sum(

        1

        for report in intelligence_reports

        if report["dependency_score"] >= 80

    )


    connected_reports = sum(

        1

        for report in intelligence_reports

        if report["connected_problems"] > 0

    )


    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "=========================================="
    )

    print(
        "MUNICIPAL PROBLEM INTELLIGENCE"
    )

    print(
        "=========================================="
    )

    print(
        "TOTAL PROBLEMS:",
        total_problems
    )

    print(
        "HIGH IMPACT:",
        high_impact
    )

    print(
        "AI ANALYZED:",
        analyzed
    )

    print(
        "CASCADING:",
        cascading
    )

    print(
        "HIGH PRIORITY:",
        high_priority
    )

    print(
        "UNASSIGNED:",
        unassigned
    )

    print(
        "DEPENDENCY ANALYZED:",
        dependency_analyzed_count
    )

    print(
        "STRONG DEPENDENCIES:",
        strong_dependencies
    )

    print(
        "CONNECTED REPORTS:",
        connected_reports
    )

    print(
        "=========================================="
    )


    # ========================================================
    # SEND DATA TO TEMPLATE
    # ========================================================

    return render_template(

        "municipality/intelligence.html",

        reports=intelligence_reports,

        total_problems=total_problems,

        high_impact=high_impact,

        analyzed=analyzed,

        cascading=cascading,

        high_priority=high_priority,

        unassigned=unassigned,

        dependency_analyzed_count=
            dependency_analyzed_count,

        strong_dependencies=
            strong_dependencies,

        connected_reports=
            connected_reports,

        active_page="intelligence",

        portal="municipality"

    )

@app.route("/municipality/dependencies")
def municipality_dependencies():

    from math import radians, sin, cos, sqrt, atan2

    # =====================================================
    # GET ALL REAL REPORTS FROM MONGODB
    # =====================================================

    reports = list(
        db.problems.find({
            "latitude": {
                "$exists": True,
                "$ne": None
            },
            "longitude": {
                "$exists": True,
                "$ne": None
            }
        }).sort("_id", -1)
    )

    # =====================================================
    # DISTANCE CALCULATION
    # =====================================================

    def calculate_distance(lat1, lon1, lat2, lon2):

        earth_radius_km = 6371.0

        d_lat = radians(lat2 - lat1)
        d_lon = radians(lon2 - lon1)

        a = (
            sin(d_lat / 2) ** 2
            +
            cos(radians(lat1))
            *
            cos(radians(lat2))
            *
            sin(d_lon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )

        return earth_radius_km * c

    # =====================================================
    # PREPARE REAL PROBLEMS
    # =====================================================

    problems = []

    for report in reports:

        try:
            latitude = float(
                report.get("latitude")
            )

            longitude = float(
                report.get("longitude")
            )

        except (TypeError, ValueError):

            continue

        title = report.get(
            "title",
            "Urban Problem"
        )

        description = report.get(
            "description",
            ""
        )

        category = report.get(
            "category",
            "General"
        )

        impact = str(
            report.get(
                "impact_level",
                "MEDIUM"
            )
        ).upper()

        status = report.get(
            "status",
            "Submitted"
        )

        root_cause = report.get(
            "root_cause",
            "Analysis pending"
        )

        cascading_effects = report.get(
            "cascading_effects",
            []
        )

        problems.append({

            "id": str(
                report["_id"]
            ),

            "title": title,

            "description": description,

            "category": category,

            "impact": impact,

            "status": status,

            "latitude": latitude,

            "longitude": longitude,

            "root_cause": root_cause,

            "cascading_effects": cascading_effects

        })

    # =====================================================
    # CLASSIFY PROBLEM TYPE
    # =====================================================

    def classify_problem(problem):

        text = (
            str(problem["title"])
            + " "
            + str(problem["description"])
            + " "
            + str(problem["category"])
        ).lower()

        if any(word in text for word in [
            "drain",
            "drainage",
            "waterlogging",
            "flood",
            "flooding",
            "stormwater"
        ]):

            return "Water & Drainage"

        if any(word in text for word in [
            "traffic",
            "congestion",
            "traffic jam",
            "junction",
            "signal"
        ]):

            return "Traffic"

        if any(word in text for word in [
            "road",
            "pothole",
            "potholes",
            "damaged road",
            "road damage"
        ]):

            return "Roads & Infrastructure"

        if any(word in text for word in [
            "garbage",
            "waste",
            "dumping",
            "trash"
        ]):

            return "Waste Management"

        if any(word in text for word in [
            "streetlight",
            "street light",
            "lighting",
            "electricity"
        ]):

            return "Electricity & Lighting"

        if any(word in text for word in [
            "park",
            "tree",
            "pollution",
            "environment"
        ]):

            return "Environment"

        return "General"

    # =====================================================
    # ASSIGN PROBLEM GROUP
    # =====================================================

    for problem in problems:

        problem["group"] = classify_problem(
            problem
        )

    # =====================================================
    # CHECK WHETHER TWO PROBLEMS CAN BE CONNECTED
    # =====================================================

    def calculate_dependency(problem_a, problem_b):

        score = 0

        # ---------------------------------------------
        # LOCATION SCORE
        # ---------------------------------------------

        distance = calculate_distance(

            problem_a["latitude"],
            problem_a["longitude"],

            problem_b["latitude"],
            problem_b["longitude"]

        )

        if distance <= 0.5:

            location_score = 30

        elif distance <= 1:

            location_score = 25

        elif distance <= 2:

            location_score = 15

        elif distance <= 5:

            location_score = 5

        else:

            location_score = 0

        score += location_score

        # ---------------------------------------------
        # CATEGORY SCORE
        # ---------------------------------------------

        group_a = problem_a["group"]
        group_b = problem_b["group"]

        category_score = 0

        # Same category
        if group_a == group_b:

            category_score = 30

        # Known urban dependency relationships
        elif (
            group_a == "Water & Drainage"
            and group_b in [
                "Roads & Infrastructure",
                "Traffic"
            ]
        ):

            category_score = 30

        elif (
            group_b == "Water & Drainage"
            and group_a in [
                "Roads & Infrastructure",
                "Traffic"
            ]
        ):

            category_score = 30

        elif (
            group_a == "Waste Management"
            and group_b == "Water & Drainage"
        ):

            category_score = 30

        elif (
            group_b == "Waste Management"
            and group_a == "Water & Drainage"
        ):

            category_score = 30

        elif (
            group_a == "Roads & Infrastructure"
            and group_b == "Traffic"
        ):

            category_score = 25

        elif (
            group_b == "Roads & Infrastructure"
            and group_a == "Traffic"
        ):

            category_score = 25

        elif (
            group_a == "Electricity & Lighting"
            and group_b == "Roads & Infrastructure"
        ):

            category_score = 15

        elif (
            group_b == "Electricity & Lighting"
            and group_a == "Roads & Infrastructure"
        ):

            category_score = 15

        score += category_score

        # ---------------------------------------------
        # TEXT / SEMANTIC SIMILARITY
        # ---------------------------------------------

        text_a = (
            problem_a["title"]
            + " "
            + problem_a["description"]
        ).lower()

        text_b = (
            problem_b["title"]
            + " "
            + problem_b["description"]
        ).lower()

        words_a = set(
            text_a.split()
        )

        words_b = set(
            text_b.split()
        )

        common_words = (
            words_a.intersection(words_b)
        )

        # Ignore very small common words
        useful_words = [
            word
            for word in common_words
            if len(word) > 3
        ]

        semantic_score = min(
            len(useful_words) * 5,
            20
        )

        score += semantic_score

        # ---------------------------------------------
        # FINAL SCORE
        # ---------------------------------------------

        score = min(
            score,
            100
        )

        return score, distance

    # =====================================================
    # CREATE DEPENDENCY CONNECTIONS
    # =====================================================

    dependencies = []

    for i in range(
        len(problems)
    ):

        for j in range(
            i + 1,
            len(problems)
        ):

            problem_a = problems[i]
            problem_b = problems[j]

            dependency_score, distance = (
                calculate_dependency(
                    problem_a,
                    problem_b
                )
            )

            # Only meaningful relationships
            if dependency_score >= 50:

                dependencies.append({

                    "source": problem_a,

                    "target": problem_b,

                    "score": dependency_score,

                    "distance": round(
                        distance,
                        2
                    )

                })

    # =====================================================
    # BUILD CONNECTED CLUSTERS
    # =====================================================

    parent = {}

    for problem in problems:

        parent[
            problem["id"]
        ] = problem["id"]

    def find_parent(problem_id):

        while parent[problem_id] != problem_id:

            parent[problem_id] = parent[
                parent[problem_id]
            ]

            problem_id = parent[
                problem_id
            ]

        return problem_id

    def union(a, b):

        root_a = find_parent(a)
        root_b = find_parent(b)

        if root_a != root_b:

            parent[root_b] = root_a

    for dependency in dependencies:

        source_id = dependency[
            "source"
        ]["id"]

        target_id = dependency[
            "target"
        ]["id"]

        union(
            source_id,
            target_id
        )

    # =====================================================
    # GROUP PROBLEMS INTO CLUSTERS
    # =====================================================

    cluster_groups = {}

    for problem in problems:

        root = find_parent(
            problem["id"]
        )

        if root not in cluster_groups:

            cluster_groups[root] = []

        cluster_groups[root].append(
            problem
        )

    # =====================================================
    # CREATE CLUSTER DATA
    # =====================================================

    clusters = []

    for cluster_items in cluster_groups.values():

        # A cluster must contain at least 2 problems
        if len(cluster_items) < 2:

            continue

        # ---------------------------------------------
        # CLUSTER IMPACT
        # ---------------------------------------------

        impact_values = []

        for problem in cluster_items:

            if problem["impact"] == "HIGH":

                impact_values.append(3)

            elif problem["impact"] == "MEDIUM":

                impact_values.append(2)

            else:

                impact_values.append(1)

        average_impact = (
            sum(impact_values)
            /
            len(impact_values)
        )

        if average_impact >= 2.5:

            cluster_impact = "HIGH"

        elif average_impact >= 1.5:

            cluster_impact = "MEDIUM"

        else:

            cluster_impact = "LOW"

        # ---------------------------------------------
        # DEPARTMENTS
        # ---------------------------------------------

        departments = set()

        for problem in cluster_items:

            group = problem["group"]

            if group == "Water & Drainage":

                departments.add(
                    "Water & Drainage"
                )

            elif group == "Roads & Infrastructure":

                departments.add(
                    "Roads"
                )

            elif group == "Traffic":

                departments.add(
                    "Traffic"
                )

            elif group == "Waste Management":

                departments.add(
                    "Waste Management"
                )

            elif group == "Electricity & Lighting":

                departments.add(
                    "Electricity"
                )

            elif group == "Environment":

                departments.add(
                    "Environment"
                )

        # ---------------------------------------------
        # FIND ROOT CAUSE
        # ---------------------------------------------

        root_cause_problem = cluster_items[0]

        for problem in cluster_items:

            text = (
                problem["title"]
                + " "
                + problem["description"]
            ).lower()

            if any(word in text for word in [
                "drain",
                "drainage",
                "blocked",
                "garbage",
                "waste",
                "pothole"
            ]):

                root_cause_problem = problem

                break

        # ---------------------------------------------
        # FIND DOWNSTREAM EFFECTS
        # ---------------------------------------------

        downstream_effects = []

        for problem in cluster_items:

            if (
                problem["id"]
                !=
                root_cause_problem["id"]
            ):

                downstream_effects.append(
                    problem
                )

        # ---------------------------------------------
        # FIND CONNECTIONS INSIDE CLUSTER
        # ---------------------------------------------

        cluster_ids = set(
            problem["id"]
            for problem in cluster_items
        )

        cluster_dependencies = [

            dependency

            for dependency in dependencies

            if (
                dependency["source"]["id"]
                in cluster_ids
                and
                dependency["target"]["id"]
                in cluster_ids
            )
        ]

        if cluster_dependencies:

            dependency_score = max(

                dependency["score"]

                for dependency
                in cluster_dependencies

            )

        else:

            dependency_score = 0

        # ---------------------------------------------
        # CLUSTER NAME
        # ---------------------------------------------

        groups = []

        for problem in cluster_items:

            if problem["group"] not in groups:

                groups.append(
                    problem["group"]
                )

        if len(groups) >= 2:

            cluster_name = (
                groups[0]
                + " & "
                + groups[1]
            )

        else:

            cluster_name = groups[0]

        # ---------------------------------------------
        # CLUSTER DESCRIPTION
        # ---------------------------------------------

        cluster_description = (

            f"{len(cluster_items)} real "
            f"citizen-reported problems "
            f"show a potential dependency "
            f"relationship based on location, "
            f"problem type and description."
        )

        # ---------------------------------------------
        # SAVE CLUSTER
        # ---------------------------------------------

        clusters.append({

            "name":
                cluster_name,

            "impact":
                cluster_impact,

            "description":
                cluster_description,

            "problems":
                cluster_items,

            "root_cause":
                root_cause_problem,

            "downstream":
                downstream_effects,

            "connections":
                len(cluster_dependencies),

            "departments":
                list(departments),

            "dependency_score":
                dependency_score

        })

    # =====================================================
    # SORT CLUSTERS BY DEPENDENCY SCORE
    # =====================================================

    clusters.sort(

        key=lambda cluster:
            cluster["dependency_score"],

        reverse=True
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    total_problems = len(
        problems
    )

    total_connections = len(
        dependencies
    )

    high_impact_clusters = len([

        cluster

        for cluster in clusters

        if cluster["impact"] == "HIGH"

    ])

    # =====================================================
    # SEND REAL DATA TO HTML
    # =====================================================

    return render_template(

        "municipality/dependencies.html",

        clusters=clusters,

        total_problems=
            total_problems,

        total_connections=
            total_connections,

        high_impact_clusters=
            high_impact_clusters,

        active_page=
            "dependencies",

        portal=
            "municipality"
    )

@app.route("/municipality/priority")
def municipality_priority():

    from math import radians, sin, cos, sqrt, atan2

    # ==========================================================
    # GET ALL REAL CITIZEN REPORTS
    # ==========================================================

    reports = list(
        db.problems.find({}).sort("_id", -1)
    )

    # ==========================================================
    # DISTANCE FUNCTION
    # Used to estimate how many nearby problems are connected
    # ==========================================================

    def calculate_distance(lat1, lon1, lat2, lon2):

        earth_radius = 6371.0

        d_lat = radians(lat2 - lat1)
        d_lon = radians(lon2 - lon1)

        a = (
            sin(d_lat / 2) ** 2
            +
            cos(radians(lat1))
            * cos(radians(lat2))
            * sin(d_lon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )

        return earth_radius * c

    # ==========================================================
    # CATEGORY -> DEPARTMENT
    # ==========================================================

    department_map = {

        "water": "Water & Drainage Department",

        "drain": "Water & Drainage Department",

        "road": "Roads & Infrastructure Department",

        "traffic": "Traffic Department",

        "waste": "Waste Management Department",

        "electricity": "Electricity & Lighting Department",

        "lighting": "Electricity & Lighting Department",

        "environment": "Environment Department"

    }

    # ==========================================================
    # GET DEPARTMENT
    # ==========================================================

    def get_department(category):

        category_text = str(
            category or ""
        ).lower()

        for keyword, department in department_map.items():

            if keyword in category_text:
                return department

        return "Municipal Administration"

    # ==========================================================
    # IMPACT SCORE
    # Based on the REAL AI impact level already stored
    # ==========================================================

    def get_impact_score(report):

        impact = str(
            report.get(
                "impact_level",
                "MEDIUM"
            )
        ).upper()

        if impact == "HIGH":
            return 90

        if impact == "MEDIUM":
            return 60

        return 30

    # ==========================================================
    # SEVERITY SCORE
    # Derived from real report title + description
    # ==========================================================

    def get_severity_score(report):

        text = (
            str(report.get("title", ""))
            + " "
            + str(report.get("description", ""))
        ).lower()

        severe_words = [
            "accident",
            "dangerous",
            "emergency",
            "hospital",
            "ambulance",
            "flood",
            "flooding",
            "critical",
            "severe",
            "life threatening",
            "major blockage",
            "blocked completely"
        ]

        high_words = [
            "waterlogging",
            "blocked drain",
            "traffic congestion",
            "pothole",
            "damaged road",
            "garbage",
            "waste dumping",
            "streetlight not working"
        ]

        severe_matches = sum(
            1
            for word in severe_words
            if word in text
        )

        high_matches = sum(
            1
            for word in high_words
            if word in text
        )

        if severe_matches >= 2:
            return 100

        if severe_matches == 1:
            return 90

        if high_matches >= 2:
            return 80

        if high_matches == 1:
            return 70

        return 50

    # ==========================================================
    # FIND REAL CONNECTED PROBLEMS
    # ==========================================================

    def get_connected_count(report):

        stored_count = report.get(
            "connected_problems"
        )

        try:

            if stored_count is not None:
                return int(stored_count)

        except (
            TypeError,
            ValueError
        ):

            pass

        return 0

    # ==========================================================
    # FIND NEARBY REPORTS
    # ==========================================================

    def get_nearby_count(report):

        try:

            latitude = float(
                report.get("latitude")
            )

            longitude = float(
                report.get("longitude")
            )

        except (
            TypeError,
            ValueError
        ):

            return 0

        count = 0

        for other in reports:

            if other.get("_id") == report.get("_id"):
                continue

            try:

                other_lat = float(
                    other.get("latitude")
                )

                other_lon = float(
                    other.get("longitude")
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            distance = calculate_distance(
                latitude,
                longitude,
                other_lat,
                other_lon
            )

            if distance <= 1.0:
                count += 1

        return count

    # ==========================================================
    # CONNECTIVITY SCORE
    # ==========================================================

    def get_connectivity_score(
        connected_count,
        nearby_count
    ):

        total_connections = (
            connected_count
            + nearby_count
        )

        return min(
            100,
            40 + (
                total_connections * 10
            )
        )

    # ==========================================================
    # AFFECTED AREA SCORE
    #
    # We do not have actual GIS affected-area polygons yet.
    # Therefore we use nearby citizen complaints as a
    # real-world proxy.
    # ==========================================================

    def get_area_score(nearby_count):

        if nearby_count >= 8:
            return 100

        if nearby_count >= 6:
            return 90

        if nearby_count >= 4:
            return 80

        if nearby_count >= 2:
            return 70

        if nearby_count == 1:
            return 50

        return 30

    # ==========================================================
    # URGENCY SCORE
    # ==========================================================

    def get_urgency_score(report):

        priority = str(
            report.get(
                "priority",
                "MEDIUM"
            )
        ).upper()

        status = str(
            report.get(
                "status",
                "Submitted"
            )
        ).lower()

        text = (
            str(report.get("title", ""))
            + " "
            + str(report.get("description", ""))
        ).lower()

        emergency_words = [
            "accident",
            "emergency",
            "ambulance",
            "hospital",
            "flood",
            "life threatening",
            "dangerous",
            "critical"
        ]

        if any(
            word in text
            for word in emergency_words
        ):
            return 100

        if priority == "HIGH":
            return 90

        if priority == "MEDIUM":
            return 65

        if "submitted" in status:
            return 55

        return 45

    # ==========================================================
    # CREATE REAL PRIORITY RECORDS
    # ==========================================================

    priority_problems = []

    for report in reports:

        title = report.get(
            "title",
            "Urban Problem"
        )

        description = report.get(
            "description",
            ""
        )

        category = report.get(
            "category",
            "General"
        )

        address = report.get(
            "address",
            report.get(
                "location",
                "Location not provided"
            )
        )

        impact_level = str(
            report.get(
                "impact_level",
                "MEDIUM"
            )
        ).upper()

        connected_count = get_connected_count(
            report
        )

        nearby_count = get_nearby_count(
            report
        )

        impact_score = get_impact_score(
            report
        )

        severity_score = get_severity_score(
            report
        )

        connectivity_score = get_connectivity_score(
            connected_count,
            nearby_count
        )

        area_score = get_area_score(
            nearby_count
        )

        urgency_score = get_urgency_score(
            report
        )

        # ======================================================
        # FINAL PRIORITY SCORE
        #
        # Impact       = 30%
        # Severity     = 20%
        # Connectivity= 20%
        # Area         = 15%
        # Urgency      = 15%
        # ======================================================

        priority_score = round(

            (
                impact_score * 0.30
            )
            +
            (
                severity_score * 0.20
            )
            +
            (
                connectivity_score * 0.20
            )
            +
            (
                area_score * 0.15
            )
            +
            (
                urgency_score * 0.15
            )

        )

        # ======================================================
        # PRIORITY LEVEL
        # ======================================================

        if priority_score >= 85:

            priority_level = "CRITICAL"

        elif priority_score >= 70:

            priority_level = "HIGH"

        elif priority_score >= 50:

            priority_level = "MEDIUM"

        else:

            priority_level = "LOW"

        # ======================================================
        # DEPARTMENT
        # ======================================================

        department = get_department(
            category
        )

        # ======================================================
        # DOWNSTREAM EFFECTS
        # Already generated by AI analysis
        # ======================================================

        cascading_effects = report.get(
            "cascading_effects",
            []
        )

        if not isinstance(
            cascading_effects,
            list
        ):
            cascading_effects = []

        # ======================================================
        # AI REASON
        # ======================================================

        if cascading_effects:

            reason = (
                "High impact with cascading effects. "
                "The problem is connected to "
                + ", ".join(
                    cascading_effects
                )
                + ". Addressing the upstream "
                "problem may reduce downstream impacts."
            )

        elif connected_count > 0:

            reason = (
                "The problem has "
                + str(connected_count)
                + " connected urban problems and "
                "may affect multiple municipal services."
            )

        elif nearby_count > 0:

            reason = (
                "Several citizen-reported problems "
                "are located nearby, indicating a "
                "potential local problem cluster."
            )

        else:

            reason = (
                "The problem currently has limited "
                "identified connections and should "
                "be reviewed based on local conditions."
            )

        # ======================================================
        # RECOMMENDED ACTION
        # ======================================================

        if priority_level == "CRITICAL":

            recommended_action = (
                "Immediate field verification and "
                "municipal intervention."
            )

        elif priority_level == "HIGH":

            recommended_action = (
                "Inspect the location and assign "
                "the responsible department."
            )

        elif priority_level == "MEDIUM":

            recommended_action = (
                "Schedule inspection and monitor "
                "the problem."
            )

        else:

            recommended_action = (
                "Monitor the report and review "
                "during routine maintenance."
            )

        priority_problems.append({

            "id": str(
                report.get("_id")
            ),

            "title": title,

            "description": description,

            "category": category,

            "address": address,

            "impact": impact_level,

            "priority": priority_level,

            "priority_score": priority_score,

            "impact_score": impact_score,

            "severity_score": severity_score,

            "connectivity_score": connectivity_score,

            "area_score": area_score,

            "urgency_score": urgency_score,

            "connected_problems": connected_count,

            "nearby_problems": nearby_count,

            "cascading_effects": cascading_effects,

            "department": department,

            "reason": reason,

            "recommended_action": recommended_action

        })

    # ==========================================================
    # SORT HIGHEST PRIORITY FIRST
    # ==========================================================

    priority_problems.sort(
        key=lambda item:
            item["priority_score"],
        reverse=True
    )

    # ==========================================================
    # ADD RANK
    # ==========================================================

    for index, problem in enumerate(
        priority_problems,
        start=1
    ):

        problem["rank"] = index

    # ==========================================================
    # SUMMARY STATISTICS
    # ==========================================================

    critical_count = sum(
        1
        for problem in priority_problems
        if problem["priority"] == "CRITICAL"
    )

    high_count = sum(
        1
        for problem in priority_problems
        if problem["priority"] == "HIGH"
    )

    interconnected_count = sum(
        1
        for problem in priority_problems
        if (
            problem["connected_problems"] > 0
            or problem["nearby_problems"] > 0
        )
    )

    high_impact_count = sum(
        1
        for problem in priority_problems
        if problem["impact"] == "HIGH"
    )

    return render_template(

        "municipality/priority.html",

        problems=priority_problems,

        total_problems=len(
            priority_problems
        ),

        critical_count=critical_count,

        high_count=high_count,

        interconnected_count=interconnected_count,

        high_impact_count=high_impact_count,

        active_page="priority",

        portal="municipality"

    )

@app.route("/municipality/interventions")
def municipality_interventions():

    # =====================================================
    # GET REAL REPORTS FROM MONGODB
    # =====================================================

    reports = list(
        db.problems.find({}).sort("_id", -1)
    )


    # =====================================================
    # DEPARTMENT MAPPING
    # =====================================================

    def get_department(category):

        category_text = str(
            category or ""
        ).lower()

        if (
            "water" in category_text
            or "drain" in category_text
            or "drainage" in category_text
        ):
            return "Water & Drainage"

        elif (
            "road" in category_text
            or "infrastructure" in category_text
        ):
            return "Roads & Infrastructure"

        elif (
            "traffic" in category_text
        ):
            return "Traffic"

        elif (
            "waste" in category_text
            or "garbage" in category_text
        ):
            return "Waste Management"

        elif (
            "electricity" in category_text
            or "lighting" in category_text
            or "streetlight" in category_text
        ):
            return "Electricity & Lighting"

        else:
            return "Municipal Services"


    # =====================================================
    # CREATE REAL INTERVENTION DATA
    # =====================================================

    interventions = []


    for report in reports:

        title = report.get(
            "title",
            "Urban Problem"
        )

        category = report.get(
            "category",
            "General"
        )

        description = report.get(
            "description",
            ""
        )

        impact = str(
            report.get(
                "impact_level",
                "MEDIUM"
            )
        ).upper()

        priority = str(
            report.get(
                "priority",
                impact
            )
        ).upper()

        status = report.get(
            "status",
            "Submitted"
        )

        progress = report.get(
            "progress",
            25
        )

        department = get_department(
            category
        )


        # =================================================
        # NORMALIZE PROGRESS
        # =================================================

        try:
            progress = int(progress)
        except (
            TypeError,
            ValueError
        ):
            progress = 25


        progress = max(
            0,
            min(
                progress,
                100
            )
        )


        # =================================================
        # DETERMINE INTERVENTION STATUS
        # =================================================

        status_lower = str(
            status
        ).lower()


        if status_lower == "resolved":

            intervention_status = "completed"
            progress = 100

        elif status_lower in [
            "assigned",
            "in progress"
        ]:

            intervention_status = "active"

        else:

            intervention_status = "pending"


        # =================================================
        # INTERVENTION TITLE
        # =================================================

        if (
            "water" in str(category).lower()
            or "drain" in str(category).lower()
            or "drainage" in str(category).lower()
        ):

            intervention_title = (
                "Drainage Infrastructure Intervention"
            )

        elif (
            "road" in str(category).lower()
            or "infrastructure" in str(category).lower()
        ):

            intervention_title = (
                "Road Infrastructure Intervention"
            )

        elif (
            "traffic" in str(category).lower()
        ):

            intervention_title = (
                "Traffic Management Intervention"
            )

        elif (
            "waste" in str(category).lower()
            or "garbage" in str(category).lower()
        ):

            intervention_title = (
                "Waste Management Intervention"
            )

        elif (
            "electricity" in str(category).lower()
            or "lighting" in str(category).lower()
            or "streetlight" in str(category).lower()
        ):

            intervention_title = (
                "Lighting Infrastructure Intervention"
            )

        else:

            intervention_title = (
                "Municipal Infrastructure Intervention"
            )


        # =================================================
        # CREATE INTERVENTION OBJECT
        # =================================================

        interventions.append({

            "id":
                str(
                    report.get(
                        "_id"
                    )
                ),

            "title":
                intervention_title,

            "problem_title":
                title,

            "description":
                description,

            "category":
                category,

            "department":
                department,

            "impact":
                impact,

            "priority":
                priority,

            "status":
                intervention_status,

            "original_status":
                status,

            "progress":
                progress,

            "address":
                report.get(
                    "address",
                    report.get(
                        "location",
                        "Location not provided"
                    )
                ),

            "root_cause":
                report.get(
                    "root_cause",
                    "Analysis pending"
                ),

            "cascading_effects":
                report.get(
                    "cascading_effects",
                    []
                ),

            "ai_explanation":
                report.get(
                    "ai_explanation",
                    "AI analysis not available."
                ),

            "created_at":
                report.get(
                    "created_at"
                )
        })


    # =====================================================
    # SUMMARY COUNTS
    # =====================================================

    active_count = sum(
        1
        for item in interventions
        if item["status"] == "active"
    )


    pending_count = sum(
        1
        for item in interventions
        if item["status"] == "pending"
    )


    completed_count = sum(
        1
        for item in interventions
        if item["status"] == "completed"
    )


    urgent_count = sum(
        1
        for item in interventions
        if item["priority"] in [
            "HIGH",
            "CRITICAL"
        ]
        and item["status"] != "completed"
    )


    departments = sorted(
        set(
            item["department"]
            for item in interventions
        )
    )


    # =====================================================
    # RENDER PAGE
    # =====================================================

    return render_template(

        "municipality/interventions.html",

        interventions=interventions,

        active_count=active_count,

        pending_count=pending_count,

        completed_count=completed_count,

        urgent_count=urgent_count,

        department_list=departments,

        department_count=len(
            departments
        ),

        total_count=len(
            interventions
        ),

        active_page="interventions",

        portal="municipality"
    )
@app.route("/municipality/map")
def municipality_map():

    # ==========================================================
    # GET ALL REAL CITIZEN REPORTS
    # ==========================================================

    reports = list(
        db.problems.find({}).sort("_id", -1)
    )

    map_problems = []

    # ==========================================================
    # CONVERT REPORTS INTO PUBLIC MAP DATA
    #
    # IMPORTANT:
    # citizen_id, name, email, phone etc. are NOT sent.
    # ==========================================================

    for report in reports:

        # ------------------------------------------------------
        # Get coordinates
        # ------------------------------------------------------

        latitude = report.get("latitude")
        longitude = report.get("longitude")

        try:

            latitude = float(latitude)
            longitude = float(longitude)

        except (
            TypeError,
            ValueError
        ):

            # Old reports without coordinates
            # cannot be displayed accurately on the map.
            continue

        # ------------------------------------------------------
        # Get public information
        # ------------------------------------------------------

        title = report.get(
            "title",
            "Urban Problem"
        )

        category = report.get(
            "category",
            "General"
        )

        address = report.get(
            "address",
            report.get(
                "location",
                "Location not provided"
            )
        )

        description = report.get(
            "description",
            ""
        )

        impact = str(
            report.get(
                "impact_level",
                "MEDIUM"
            )
        ).upper()

        priority = str(
            report.get(
                "priority",
                impact
            )
        ).upper()

        status = report.get(
            "status",
            "Submitted"
        )

        connected = report.get(
            "connected_problems",
            0
        )

        cascading_effects = report.get(
            "cascading_effects",
            []
        )

        # ------------------------------------------------------
        # Department
        # ------------------------------------------------------

        category_text = str(
            category
        ).lower()

        if (
            "water" in category_text
            or "drain" in category_text
        ):

            department = "Water & Drainage"

        elif "road" in category_text:

            department = "Roads & Infrastructure"

        elif "traffic" in category_text:

            department = "Traffic"

        elif (
            "waste" in category_text
            or "garbage" in category_text
        ):

            department = "Waste Management"

        elif (
            "electricity" in category_text
            or "lighting" in category_text
        ):

            department = "Electricity & Lighting"

        elif "environment" in category_text:

            department = "Environment"

        else:

            department = "Municipal Administration"

        # ------------------------------------------------------
        # Add public map problem
        # ------------------------------------------------------

        map_problems.append({

            "id": str(
                report.get("_id")
            ),

            "title": title,

            "description": description,

            "category": category,

            "address": address,

            "impact": impact,

            "priority": priority,

            "status": status,

            "department": department,

            "connected_problems": connected,

            "cascading_effects": cascading_effects,

            "latitude": latitude,

            "longitude": longitude

        })

    # ==========================================================
    # SUMMARY DATA
    # ==========================================================

    total_problems = len(
        map_problems
    )

    high_impact = sum(
        1
        for problem in map_problems
        if problem["impact"] == "HIGH"
    )

    medium_impact = sum(
        1
        for problem in map_problems
        if problem["impact"] == "MEDIUM"
    )

    low_impact = sum(
        1
        for problem in map_problems
        if problem["impact"] == "LOW"
    )

    # ==========================================================
    # HOTSPOTS
    #
    # Simple real calculation:
    # locations having 2 or more reports within
    # approximately 1 km are considered clusters.
    # ==========================================================

    from math import radians, sin, cos, sqrt, atan2

    def calculate_distance(
        lat1,
        lon1,
        lat2,
        lon2
    ):

        earth_radius = 6371.0

        d_lat = radians(
            lat2 - lat1
        )

        d_lon = radians(
            lon2 - lon1
        )

        a = (
            sin(d_lat / 2) ** 2
            +
            cos(radians(lat1))
            *
            cos(radians(lat2))
            *
            sin(d_lon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )

        return earth_radius * c

    hotspot_count = 0

    for problem in map_problems:

        nearby_count = 0

        for other in map_problems:

            if problem["id"] == other["id"]:
                continue

            distance = calculate_distance(

                problem["latitude"],
                problem["longitude"],

                other["latitude"],
                other["longitude"]

            )

            if distance <= 1.0:

                nearby_count += 1

        if nearby_count >= 2:

            hotspot_count += 1

    # Avoid counting the same cluster multiple times
    hotspot_count = min(
        hotspot_count,
        total_problems
    )

    # ==========================================================
    # DEPARTMENTS
    # ==========================================================

    departments = set()

    for problem in map_problems:

        departments.add(
            problem["department"]
        )

    department_count = len(
        departments
    )

    # ==========================================================
    # RENDER
    # ==========================================================

    return render_template(

        "municipality/map.html",

        problems=map_problems,

        total_problems=total_problems,

        high_impact=high_impact,

        medium_impact=medium_impact,

        low_impact=low_impact,

        hotspot_count=hotspot_count,

        department_count=department_count,

        active_page="map",

        portal="municipality"

    )

@app.route("/municipality/departments")
def municipality_departments():
    return render_template(
        "municipality/departments.html",
        active_page="departments",
        portal="municipality"
    )

@app.route("/test-db")
def test_db():

    try:
        db.command("ping")

        return "MongoDB connected successfully!"

    except Exception as e:

        return f"MongoDB connection failed: {e}"

@app.route("/debug/reports")
def debug_reports():

    reports = list(
        db.problems.find({}).sort("_id", -1)
    )

    for report in reports:

        print("======================================")
        print("ID:", report.get("_id"))
        print("TITLE:", report.get("title"))
        print("ADDRESS:", report.get("address"))
        print("CATEGORY:", report.get("category"))
        print("STATUS:", report.get("status"))
        print("IMPACT:", report.get("impact_level"))
        print("PRIORITY:", report.get("priority"))
        print("AI ANALYZED:", report.get("ai_analyzed"))
        print("ROOT CAUSE:", report.get("root_cause"))
        print("======================================")

    return "Check Terminal" 

@app.route("/api/reverse-geocode")
def reverse_geocode():

    try:
        latitude = float(
            request.args.get("latitude")
        )

        longitude = float(
            request.args.get("longitude")
        )

    except (TypeError, ValueError):

        return jsonify({
            "address": None,
            "error": "Invalid coordinates"
        }), 400


    try:

        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "jsonv2",
                "lat": latitude,
                "lon": longitude,
                "zoom": 18,
                "addressdetails": 1
            },
            headers={
                "User-Agent":
                    "UrbanNexus/1.0"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        address = data.get(
            "display_name"
        )

        if not address:
            address = (
                f"{latitude:.6f}, "
                f"{longitude:.6f}"
            )

        return jsonify({
            "address": address,
            "latitude": latitude,
            "longitude": longitude
        })


    except requests.RequestException as error:

        print(
            "REVERSE GEOCODING ERROR:",
            error
        )

        return jsonify({
            "address":
                f"{latitude:.6f}, {longitude:.6f}",
            "latitude": latitude,
            "longitude": longitude
        })

@app.route("/api/geocode")
def geocode():

    query = request.args.get(
        "q",
        ""
    ).strip()


    if not query:

        return jsonify([])


    try:

        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "format": "jsonv2",
                "q": query,
                "countrycodes": "in",
                "limit": 5,
                "addressdetails": 1
            },
            headers={
                "User-Agent":
                    "UrbanNexus/1.0"
            },
            timeout=10
        )


        response.raise_for_status()


        results = response.json()


        locations = []


        for result in results:

            try:

                latitude = float(
                    result["lat"]
                )

                longitude = float(
                    result["lon"]
                )

            except (
                KeyError,
                TypeError,
                ValueError
            ):

                continue


            locations.append({

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "address":
                    result.get(
                        "display_name",
                        query
                    )

            })


        return jsonify(
            locations
        )


    except requests.RequestException as error:

        print(
            "GEOCODING ERROR:",
            error
        )

        return jsonify({
            "error":
                "Unable to search location"
        }), 500
@app.route("/citizen/nearby-problems")
def citizen_nearby_problems():

    from math import radians, sin, cos, sqrt, atan2

    # =====================================================
    # GET SELECTED LOCATION
    # =====================================================

    try:

        latitude = float(
            request.args.get("latitude")
        )

        longitude = float(
            request.args.get("longitude")
        )

    except (TypeError, ValueError):

        return jsonify({
            "problems": [],
            "all_problems": [],
            "error": "Invalid location"
        }), 400


    # =====================================================
    # NEARBY SEARCH RADIUS
    # 5 KILOMETERS
    # =====================================================

    radius_km = 5.0


    # =====================================================
    # GET ALL REPORTS HAVING LOCATION
    #
    # We do NOT filter by citizen_id.
    #
    # Therefore:
    # - Your complaints
    # - Other citizens' complaints
    #
    # can appear.
    # =====================================================

    reports = list(
        db.problems.find({
            "latitude": {
                "$exists": True,
                "$ne": None
            },

            "longitude": {
                "$exists": True,
                "$ne": None
            }
        })
        .sort(
            "_id",
            -1
        )
    )


    # =====================================================
    # DISTANCE CALCULATION
    # =====================================================

    def calculate_distance(
        lat1,
        lon1,
        lat2,
        lon2
    ):

        earth_radius_km = 6371.0


        d_lat = radians(
            lat2 - lat1
        )

        d_lon = radians(
            lon2 - lon1
        )


        a = (
            sin(d_lat / 2) ** 2
            +
            cos(radians(lat1))
            *
            cos(radians(lat2))
            *
            sin(d_lon / 2) ** 2
        )


        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )


        return earth_radius_km * c


    # =====================================================
    # CREATE LISTS
    # =====================================================

    all_problems = []

    nearby_problems = []


    # =====================================================
    # PROCESS EVERY REPORT
    # =====================================================

    for report in reports:

        try:

            report_lat = float(
                report.get(
                    "latitude"
                )
            )

            report_lon = float(
                report.get(
                    "longitude"
                )
            )

        except (
            TypeError,
            ValueError
        ):

            continue


        # =================================================
        # CALCULATE DISTANCE
        # =================================================

        distance = calculate_distance(
            latitude,
            longitude,
            report_lat,
            report_lon
        )


        # =================================================
        # PUBLIC REPORT INFORMATION ONLY
        #
        # DO NOT RETURN:
        # - citizen_id
        # - citizen name
        # - email
        # - phone
        # =================================================

        problem = {

            "id":
                str(
                    report.get(
                        "_id"
                    )
                ),

            "title":
                report.get(
                    "title",
                    "Urban Problem"
                ),

            "description":
                report.get(
                    "description",
                    ""
                ),

            "category":
                report.get(
                    "category",
                    "General"
                ),

            "address":
                report.get(
                    "address",
                    report.get(
                        "location",
                        "Location not provided"
                    )
                ),

            "impact_level":
                str(
                    report.get(
                        "impact_level",
                        "MEDIUM"
                    )
                ).upper(),

            "status":
                report.get(
                    "status",
                    "Submitted"
                ),

            "latitude":
                report_lat,

            "longitude":
                report_lon,

            "distance_km":
                round(
                    distance,
                    3
                )

        }


        # =================================================
        # ADD TO ALL PROBLEMS
        #
        # These will appear on the REAL MAP.
        # =================================================

        all_problems.append(
            problem
        )


        # =================================================
        # ADD TO NEARBY PROBLEMS
        #
        # These will appear in the Nearby Reports list.
        # =================================================

        if distance <= radius_km:

            nearby_problems.append(
                problem.copy()
            )


    # =====================================================
    # SORT NEARBY PROBLEMS
    # CLOSEST FIRST
    # =====================================================

    nearby_problems.sort(
        key=lambda problem:
            problem["distance_km"]
    )


    # =====================================================
    # FORMAT DISTANCE FOR ALL MAP PROBLEMS
    # =====================================================

    for problem in all_problems:

        distance = problem["distance_km"]


        if distance < 1:

            problem["distance"] = (
                f"{distance * 1000:.0f} m"
            )

        else:

            problem["distance"] = (
                f"{distance:.2f} km"
            )


    # =====================================================
    # FORMAT DISTANCE FOR NEARBY REPORTS
    # =====================================================

    for problem in nearby_problems:

        distance = problem["distance_km"]


        if distance < 1:

            problem["distance"] = (
                f"{distance * 1000:.0f} m"
            )

        else:

            problem["distance"] = (
                f"{distance:.2f} km"
            )


    # =====================================================
    # RETURN DATA TO FRONTEND
    # =====================================================

    return jsonify({

        # Nearby Reports panel
        "problems":
            nearby_problems[:20],

        # Real map
        # ALL reports having coordinates
        "all_problems":
            all_problems,

        # Selected/current location
        "location": {

            "latitude":
                latitude,

            "longitude":
                longitude

        },

        # Search radius
        "radius_km":
            radius_km

    })


@app.route("/debug-location-data")
def debug_location_data():

    reports = list(
        db.problems.find(
            {},
            {
                "_id": 1,
                "title": 1,
                "address": 1,
                "location": 1,
                "latitude": 1,
                "longitude": 1
            }
        ).sort(
            "_id",
            -1
        )
    )

    result = []

    for report in reports:

        result.append({

            "id": str(
                report.get("_id")
            ),

            "title":
                report.get(
                    "title",
                    "No title"
                ),

            "address":
                report.get(
                    "address",
                    report.get(
                        "location",
                        "No address"
                    )
                ),

            "latitude":
                report.get(
                    "latitude"
                ),

            "longitude":
                report.get(
                    "longitude"
                )

        })

    return jsonify(result)  
@app.route("/fix-old-locations")
def fix_old_locations():

    import requests
    import time

    # =====================================================
    # FIND REPORTS WITHOUT LATITUDE/LONGITUDE
    # =====================================================

    reports = list(
        db.problems.find({
            "$or": [
                {
                    "latitude": {
                        "$exists": False
                    }
                },
                {
                    "longitude": {
                        "$exists": False
                    }
                },
                {
                    "latitude": None
                },
                {
                    "longitude": None
                }
            ]
        })
    )

    updated = 0
    failed = 0

    results = []

    # =====================================================
    # PROCESS EACH OLD REPORT
    # =====================================================

    for report in reports:

        address = report.get(
            "address",
            report.get(
                "location",
                ""
            )
        )

        # =================================================
        # NO ADDRESS
        # =================================================

        if not address:

            failed += 1

            results.append({
                "title": report.get(
                    "title",
                    "Unknown Problem"
                ),

                "status": "No address"
            })

            continue

        # =================================================
        # GEOCODE ADDRESS
        # =================================================

        try:

            response = requests.get(

                "https://nominatim.openstreetmap.org/search",

                params={
                    "q": address,
                    "format": "json",
                    "limit": 1,
                    "countrycodes": "in"
                },

                headers={
                    "User-Agent":
                        "UrbanNexus/1.0"
                },

                timeout=10
            )

            data = response.json()

            # =============================================
            # LOCATION NOT FOUND
            # =============================================

            if not data:

                failed += 1

                results.append({

                    "title":
                        report.get(
                            "title",
                            "Unknown Problem"
                        ),

                    "address":
                        address,

                    "status":
                        "Location not found"
                })

                time.sleep(1)

                continue

            # =============================================
            # GET COORDINATES
            # =============================================

            latitude = float(
                data[0]["lat"]
            )

            longitude = float(
                data[0]["lon"]
            )

            # =============================================
            # UPDATE MONGODB
            # =============================================

            db.problems.update_one(

                {
                    "_id":
                        report["_id"]
                },

                {
                    "$set": {

                        "latitude":
                            latitude,

                        "longitude":
                            longitude

                    }
                }
            )

            updated += 1

            results.append({

                "title":
                    report.get(
                        "title",
                        "Unknown Problem"
                    ),

                "address":
                    address,

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "status":
                    "Updated"
            })

            print(
                "LOCATION UPDATED:"
            )

            print(
                "TITLE:",
                report.get(
                    "title",
                    "Unknown Problem"
                )
            )

            print(
                "LATITUDE:",
                latitude
            )

            print(
                "LONGITUDE:",
                longitude
            )

            print(
                "--------------------------------"
            )

            # =============================================
            # WAIT BETWEEN NOMINATIM REQUESTS
            # =============================================

            time.sleep(1)

        except Exception as error:

            failed += 1

            print(
                "GEOCODING ERROR:",
                error
            )

            results.append({

                "title":
                    report.get(
                        "title",
                        "Unknown Problem"
                    ),

                "address":
                    address,

                "status":
                    "Geocoding error"
            })

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return jsonify({

        "message":
            "Old complaint location update completed.",

        "total_found":
            len(reports),

        "updated":
            updated,

        "failed":
            failed,

        "results":
            results

    })


@app.route("/municipality/problem/<report_id>")
def municipality_problem(report_id):

    from bson.objectid import ObjectId
    from bson.errors import InvalidId

    try:
        object_id = ObjectId(report_id)

    except InvalidId:
        return "Invalid problem ID", 400


    problem = db.problems.find_one({
        "_id": object_id
    })


    if not problem:
        return "Problem not found", 404


    return render_template(
        "municipality/problem_details.html",
        problem=problem,
        portal="municipality",
        active_page="intelligence"
    )


@app.route("/municipality/analyze-dependencies")
def municipality_analyze_dependencies():

    reports = list(
        db.problems.find({})
    )

    analyzed_count = 0

    for report in reports:

        analysis = analyze_dependencies(
            report,
            reports
        )

        db.problems.update_one(
            {
                "_id": report["_id"]
            },
            {
                "$set": {
                    "dependency_score":
                        analysis[
                            "dependency_score"
                        ],

                    "dependencies":
                        analysis[
                            "dependencies"
                        ],

                    "root_cause":
                        analysis[
                            "root_cause"
                        ],

                    "root_cause_type":
                        analysis[
                            "root_cause_type"
                        ],

                    "cascading_effects":
                        analysis[
                            "cascading_effects"
                        ],

                    "dependency_analyzed":
                        True,

                    "dependency_analyzed_at":
                        datetime.utcnow()
                }
            }
        )

        analyzed_count += 1

    return f"""
    <h2>UrbanNexus Dependency Analysis Completed</h2>

    <p>
        Reports analyzed:
        <strong>{analyzed_count}</strong>
    </p>

    <p>
        Dependency relationships have been
        calculated and stored in MongoDB.
    </p>

    <p>
        Next step:
        connect the results to the
        Dependency Analysis dashboard.
    </p>
    """
# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)