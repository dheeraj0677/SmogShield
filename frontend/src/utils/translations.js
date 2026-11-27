export const ADVISORY_TRANSLATIONS = {
  en: {
    label: 'English',
    dir: 'ltr',
    heading: 'Emergency Family Smog Advisory',
    good: 'Air quality is clean today. Ventilate rooms midday and enjoy outdoor walking or cycling.',
    moderate:
      'Air quality is acceptable, though sensitive children and asthma patients should avoid prolonged roadside exertion.',
    high: 'High winter smog risk. Shift workouts indoors, run HEPA or DIY box-fan filters, wear a snug N95 outdoors, and keep windows sealed during rush hours.',
  },
  hi: {
    label: 'हिन्दी (Hindi)',
    dir: 'ltr',
    heading: 'परिवार के लिए स्मॉग आपातकालीन सलाह',
    good: 'आज हवा की गुणवत्ता स्वच्छ है। दोपहर में खिड़कियाँ खोलकर वेंटिलेशन करें और बाहर टहलने का आनंद लें।',
    moderate:
      'हवा सामान्य है, लेकिन बच्चों और अस्थमा रोगियों को मुख्य सड़कों के पास लंबे समय तक व्यायाम से बचना चाहिए।',
    high: 'गंभीर शीतकालीन स्मॉग अलर्ट। बाहर व्यायाम बंद करें, घर में HEPA या DIY बॉक्स-फैन फ़िल्टर चलाएँ, बाहर निकलते समय N95 मास्क पहनें और पीक ट्रैफिक में खिड़कियाँ बंद रखें।',
  },
  ur: {
    label: 'اردو (Urdu • RTL)',
    dir: 'rtl',
    heading: 'خاندان کے لیے اسموگ ہنگامی ہدایت نامہ',
    good: 'آج ہوا کا معیار صاف ہے۔ دوپہر کے وقت کھڑکیاں کھول کر تازہ ہوا اندر آنے دیں۔',
    moderate:
      'ہوا کا معیار معتدل ہے، تاہم بچوں اور دمہ کے مریضوں کو مصروف سڑکوں کے قریب ورزش سے گریز کرنا چاہیے۔',
    high: 'شدید سردیوں کا اسموگ الرٹ۔ گھر کے اندر HEPA یا DIY فلٹر چلائیں، باہر جاتے وقت N95 ماسک پہنیں، اور رش کے اوقات میں کھڑکیاں بند رکھیں۔',
  },
  es: {
    label: 'Español (Spanish)',
    dir: 'ltr',
    heading: 'Aviso Familiar de Emergencia por Smog',
    good: 'La calidad del aire es saludable hoy. Ventile su hogar al mediodía y disfrute actividades al aire libre.',
    moderate:
      'Calidad del aire moderada; niños y personas con asma deben limitar el esfuerzo prolongado cerca del tráfico.',
    high: 'Alerta alta de smog invernal. Ejercítese en interiores, use filtro HEPA o ventilador DIY, use mascarilla N95 afuera y selle ventanas en hora pico.',
  },
};

export const COMMUNITY_PLEDGES = [
  {
    id: 'pledge-zero-burn',
    title: 'Zero-Burn Neighborhood Pledge',
    description: 'Commit to composting dry garden leaves and never burning trash or open biomass.',
    co2_kg_saved: 1.8,
    pm25_g_prevented: 18,
  },
  {
    id: 'pledge-metro-carpool',
    title: 'Metro / 3-Person School & Office Carpool',
    description: 'Replace solo petrol/diesel rides with electric transit or shared rides 3+ days/week.',
    co2_kg_saved: 2.3,
    pm25_g_prevented: 12,
  },
  {
    id: 'pledge-no-idling',
    title: 'Zero-Idling School Gate & Errands Pledge',
    description: 'Turn off vehicle engines at school pick-up zones and batch neighborhood errands.',
    co2_kg_saved: 1.1,
    pm25_g_prevented: 9,
  },
  {
    id: 'pledge-clean-cooking',
    title: 'Clean Ventilation & Lid-On Cooking Pledge',
    description: 'Avoid indoor incense/candles on smog days and run exhaust fans while cooking.',
    co2_kg_saved: 0.5,
    pm25_g_prevented: 7,
  },
];
