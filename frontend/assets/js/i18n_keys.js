/**
 * WariSeva Multilingual Foundation Translation Keys (i18n)
 * Supports English (en), Marathi (mr), Hindi (hi) for Wari Medical Emergency Module
 */

const I18N_DICTIONARY = {
  en: {
    "medical.report_emergency": "Report Medical Emergency",
    "medical.critical_case": "CRITICAL MEDICAL EMERGENCY",
    "medical.nearest_camp": "Nearby Medical Camps & Hospitals",
    "medical.select_patient": "Select Patient",
    "medical.emergency_type": "Emergency Category",
    "medical.symptoms": "Symptoms & Conditions",
    "medical.location": "Emergency Location & Zone",
    "medical.severity": "Reported Severity",
    "medical.review_submit": "Review & Dispatch Emergency",
    "medical.request_ambulance": "🚑 Request Ambulance",
    "medical.status_reported": "REPORTED",
    "medical.status_triage": "TRIAGE",
    "medical.status_assigned": "ASSIGNED",
    "medical.status_responding": "RESPONDING",
    "medical.status_arrived": "ARRIVED",
    "medical.status_treatment": "TREATMENT",
    "medical.status_referred": "REFERRED",
    "medical.status_resolved": "RESOLVED"
  },
  mr: {
    "medical.report_emergency": "वैद्यकीय आणीबाणी नोंदवा",
    "medical.critical_case": "अतिदक्षता आणीबाणी (क्रिटिकल)",
    "medical.nearest_camp": "जवळचे वैद्यकीय छावणी व रुग्णालय",
    "medical.select_patient": "रुग्ण निवडा",
    "medical.emergency_type": "आणीबाणीचा प्रकार",
    "medical.symptoms": "लक्षणे",
    "medical.location": "स्थान व मार्ग विभाग",
    "medical.severity": "गंभीरता",
    "medical.review_submit": "समीक्षा व पाठवा",
    "medical.request_ambulance": "<ctrl42> ॲम्बुलन्स मागवा",
    "medical.status_reported": "नोंदवले",
    "medical.status_triage": "तपासणी",
    "medical.status_assigned": "सोपवले",
    "medical.status_responding": "मार्गस्थ",
    "medical.status_arrived": "पोहोचले",
    "medical.status_treatment": "उपचार सुरू",
    "medical.status_referred": "संदर्भित",
    "medical.status_resolved": "सोडवले"
  },
  hi: {
    "medical.report_emergency": "चिकित्सा आपात स्थिति रिपोर्ट करें",
    "medical.critical_case": "गंभीर आपात स्थिति",
    "medical.nearest_camp": "निकटतम चिकित्सा शिविर और अस्पताल",
    "medical.select_patient": "मरीज़ चुनें",
    "medical.emergency_type": "आपात श्रेणी",
    "medical.symptoms": "लक्षण",
    "medical.location": "स्थान और ज़ोन",
    "medical.severity": "गंभीरता",
    "medical.review_submit": "समीक्षा और जमा करें",
    "medical.request_ambulance": "🚑 एम्बुलेंस का अनुरोध करें",
    "medical.status_reported": "रिपोर्ट किया गया",
    "medical.status_triage": "जाँच",
    "medical.status_assigned": "आवंटित",
    "medical.status_responding": "रवाना",
    "medical.status_arrived": "पहुँच गए",
    "medical.status_treatment": "उपचार जारी",
    "medical.status_referred": "रेफर किया गया",
    "medical.status_resolved": "हल हुआ"
  }
};

function getTranslation(key, lang = 'en') {
  return (I18N_DICTIONARY[lang] && I18N_DICTIONARY[lang][key]) || (I18N_DICTIONARY['en'][key]) || key;
}
