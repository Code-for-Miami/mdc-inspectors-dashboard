 # -*- coding: utf-8 -*-

import arrow
import datetime
import json

from flask.ext.login import login_required

from flask import (
    Blueprint, render_template
)

from feedback.dashboard.vendorsurveys import (
    get_rating_scale, get_surveys_by_role,
    get_surveys_by_completion,
    get_all_survey_responses, get_rating_by_lang,
    get_rating_by_role
)

from feedback.surveys.constants import SURVEY_DAYS
from feedback.surveys.models import Survey


from feedback.dashboard.permits import (
    api_health, get_lifespan,
    get_permit_types, trade,
    get_master_permit_counts,
    dump_socrata_api
)

blueprint = Blueprint(
    "dashboard", __name__,
    template_folder='../templates',
    static_folder="../static"
)


def to_bucket(str_date):
    ''' Converts the DB string time to a MM-DD string format.
    '''
    result = arrow.get(str_date)
    return result.strftime("%m-%d")


@blueprint.route("/", methods=["GET", "POST"])
def home():

    json_obj = {}

    surveys_by_date = {}
    surveys_date_array = []
    surveys_value_array = []

    for i in range(SURVEY_DAYS, -1, -1):
        time_i = (datetime.date.today() - datetime.timedelta(i))
        date_index = time_i.strftime("%m-%d")
        surveys_by_date[date_index] = 0
        surveys_date_array.append(date_index)

    survey_table = get_all_survey_responses(SURVEY_DAYS)

    sms_rows = [x.lang for x in survey_table if x.method == 'sms']
    web_rows = [x.lang for x in survey_table if x.method == 'web']

    # ANALYTICS CODE
    for i in range(SURVEY_DAYS, -1, -1):
        time_i = (datetime.date.today() - datetime.timedelta(i))
        date_index = time_i.strftime("%m-%d")
        surveys_value_array.append(
            len([x for x in survey_table if to_bucket(x.date_submitted) == date_index]))

    dashboard_collection = [
        {
            "id": "graph",
            "title": "Surveys Submitted - Last {0} Days".format(SURVEY_DAYS),
            "data": {
                "graph": {
                    "datetime": {
                        "data": surveys_date_array
                    },
                    "series": [
                        {
                            "data": surveys_value_array
                        }
                    ]
                }
            }
        },
        {
            "title": "Satisfaction Rating - Last {0} Days".format(SURVEY_DAYS),
            "data": "{0:.2f}".format(get_rating_scale(survey_table))
        },
        {
            "title": "Survey Type - Last {0} Days".format(SURVEY_DAYS),
            "data": {
                "web_en": web_rows.count('en'),
                "web_es": web_rows.count('es'),
                "sms_en": sms_rows.count('en'),
                "sms_es": sms_rows.count('es')
            },
            "labels": {
                "web_en": "Web (English)",
                "web_es": "Web (Spanish)",
                "sms_en": "Text (English)",
                "sms_es": "Text (Spanish)"
            }
        },
        {
            "title": "Commercial",
            "data": {
                "nc": get_lifespan('nc'),
                "rc": get_lifespan('rc'),
                "s":  get_lifespan('s')
            }
        },
        {
            "title": "Residential",
            "data": {
                "nr": get_lifespan('nr'),
                "rr": get_lifespan('rr'),
                "p":  get_lifespan('p'),
                "f":  get_lifespan('f'),
                "e":  get_lifespan('e')
            }
        },
        {
            "title": "Average time from application date to permit issuance, Owner/Builder Permits, Last 30 Days",
            "data": 0
        },
        {
            "title": "Same Day Trade Permits",
            "data": {
                "PLUM": trade(30, 'PLUM'),
                "BLDG": trade(30, 'BLDG'),
                "ELEC": trade(30, 'ELEC'),
                "FIRE": trade(30, 'FIRE'),
                "ZIPS": trade(30, 'ZIPS')
            }
        },
        {
            "title": "(UNUSED) Avg Cost of an Open Residential Permit",
            "data": 0
        },
        {
            "title": "(UNUSED) Avg Cost of an Owner/Builder Permit",
            "data": 0
        },
        {
            "title": "Permits & sub-permits issued by type, Last 30 Days",
            "data": get_permit_types()
        },
        {
            "title": "Surveys by Survey Role",
            "data": get_surveys_by_role(survey_table)
        },
        {
            "title": "Master Permits Issued, Last 30 Days",
            "data": get_master_permit_counts('permit_issued_date')
        },
        {
            "title": "How many completions?",
            "data": get_surveys_by_completion(survey_table)
        },
        {
            "title": "Purpose",
            "data": 0
        },
        {
            "title": "Ratings",
            "data": {
                "en": get_rating_by_lang(survey_table, 'en'),
                "es": get_rating_by_lang(survey_table, 'es'),
                "p1": 0,
                "p2": 0,
                "p3": 0,
                "p4": 0,
                "p5": 0,
                "contractor": get_rating_by_role(survey_table, 1),
                "architect": get_rating_by_role(survey_table, 2),
                "permitconsultant": get_rating_by_role(survey_table, 3),
                "homeowner": get_rating_by_role(survey_table, 4),
                "bizowner": get_rating_by_role(survey_table, 5)
            }
        }
    ]

    json_obj['daily_graph'] = json.dumps(dashboard_collection[0]['data']['graph'])
    json_obj['surveys_type'] = json.dumps(dashboard_collection[2])
    json_obj['permits_type'] = json.dumps(dashboard_collection[9])
    json_obj['survey_role'] = json.dumps(dashboard_collection[10])
    json_obj['survey_complete'] = json.dumps(dashboard_collection[12])
    json_obj['permits_rawjson'] = json.dumps(dump_socrata_api('p'))
    json_obj['violations_rawjson'] = json.dumps(dump_socrata_api('v'))
    json_obj['violations_locations_json'] = json.dumps(dump_socrata_api('vl'))
    json_obj['violations_type_json'] = json.dumps(dump_socrata_api('vt'))
    json_obj['violations_per_month_json'] = json.dumps(dump_socrata_api('vm'))

    today = datetime.date.today()

    return render_template(
        "public/home.html",
        api=api_health(),
        date=today.strftime('%B %d, %Y'),
        json_obj=json_obj,
        dash_obj=dashboard_collection,
        resp_obj=survey_table,
        title='Dashboard'
        )


@blueprint.route('/dashboard/feedback/', methods=['GET'])
def all_surveys():
    survey_table = get_all_survey_responses(SURVEY_DAYS)

    return render_template(
        "dashboard/all-surveys.html",
        resp_obj=survey_table,
        title='All Survey Responses'
    )


@blueprint.route('/dashboard/feedback/<id>', methods=['GET'])
@login_required
def survey_detail(id):
    survey = Survey.query.filter_by(id=id)
    return render_template(
        "dashboard/survey-detail.html",
        resp_obj=survey,
        title='Permitting & Inspection Center User Survey Metrics: Detail')


@blueprint.route("/dashboard/violations/",  methods=['GET'])
def violations_detail():
    json_obj = {}
    json_obj['violations_type_json'] = json.dumps(dump_socrata_api('vt'))
    return render_template(
        "public/violations-detail.html",
        title='Violations by Type: Detail',
        json_obj=json_obj)
