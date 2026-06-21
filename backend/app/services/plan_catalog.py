PLANS = {
    "FREE": {
        "max_users": 1,
        "max_leads": 250,
        "max_ai_requests": 100,
        "max_whatsapp_campaigns": 0,
        "max_email_campaigns": 0,
    },
    "STARTER": {
        "max_users": 5,
        "max_leads": 5000,
        "max_ai_requests": 1000,
        "max_whatsapp_campaigns": 100,
        "max_email_campaigns": 500,
    },
    "PRO": {
        "max_users": 20,
        "max_leads": 50000,
        "max_ai_requests": 10000,
        "max_whatsapp_campaigns": 1000,
        "max_email_campaigns": 10000,
    },
    "AGENCY": {
        "max_users": 100,
        "max_leads": 250000,
        "max_ai_requests": 50000,
        "max_whatsapp_campaigns": 5000,
        "max_email_campaigns": 50000,
    },
    "ENTERPRISE": {
        "max_users": 999999,
        "max_leads": 999999,
        "max_ai_requests": 999999,
        "max_whatsapp_campaigns": 999999,
        "max_email_campaigns": 999999,
    },
}


def get_plan(plan_name: str):
    return PLANS.get(
        plan_name.upper()
    )
