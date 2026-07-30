#!/usr/bin/env python3
"""
Regenerate C2 passage text with substantive, topic-specific, C2-register content.

Only passage.sections[].text and passage.full_text are rewritten. Everything
else in each file (questions, answer_key, metadata, topic info) is preserved
exactly as it already validates against the question bank.
"""

import json
import glob
import os

HEADINGS = ["Background", "How it operates", "Evidence and experience", "Challenges", "Next steps"]

ANGLE_ORDER = [
    "origins_and_daily_operation",
    "benefits_and_unexpected_costs",
    "measurement_and_evidence",
    "future_choices_and_governance",
]

# Domains in the same order as the four files for each topic appear on disk.
DOMAINS = [
    {
        "subject": "community learning centres",
        "actors": "volunteer tutors, adult learners, and part-time coordinators",
        "origin": "a retired teacher began running free tutoring sessions in a borrowed shop before the local council eventually supplied proper premises",
        "daily_mechanism": "a loose timetable of drop-in sessions rather than fixed terms, so people can arrive after shift work ends",
        "funding_model": "a patchwork of short-term grants, room-hire income, and small council subsidies",
        "benefit_primary": "adult learners who left school early have shown measurable gains in literacy and digital confidence",
        "hidden_cost": "the informality that draws people in also makes attendance hard to sustain, so the learners who most need continuity are often the first to drift away",
        "evidence_tool": "attendance registers, before-and-after skills assessments, and interviews conducted six months after each course",
        "evidence_dispute": "the learners who bother to complete a follow-up survey tend to be the more confident ones, which inflates the apparent success rate",
        "governance_body": "a rotating panel of coordinators and elected learner representatives",
        "tension": "accessibility and continuity pull in opposite directions, since the openness that attracts new learners undermines the stability that sustained progress actually requires",
        "future_choice": "the choice between introducing paid short courses that reduce dependence on grants and preserving free access at the cost of slower growth",
        "scaleup_risk": "standardising the curriculum to expand faster would strip out the responsiveness that attracted learners in the first place",
    },
    {
        "subject": "river restoration projects",
        "actors": "ecologists, landowners, and volunteer river wardens",
        "origin": "a group of anglers first lobbied to remove a derelict weir, and only later did a formal restoration partnership take shape around their campaign",
        "daily_mechanism": "seasonal cycles of bank planting, sediment monitoring, and invasive-species clearance timed around spawning periods",
        "funding_model": "a mix of agri-environment grants, water-company offset payments, and one-off lottery awards",
        "benefit_primary": "fish populations and riverside biodiversity have recovered noticeably in stretches where channels were reconnected to their floodplains",
        "hidden_cost": "removing a barrier upstream can shift flooding risk onto communities downstream who were never consulted about the change",
        "evidence_tool": "fish counts, water-quality samples, and satellite images of floodplain vegetation taken before and after each intervention",
        "evidence_dispute": "natural year-to-year variation in rainfall and river flow can produce changes that look like restoration outcomes but are not",
        "governance_body": "a catchment partnership board made up of landowners, regulators, and conservation charities",
        "tension": "restoring a river to something resembling its natural state can conflict with the flood protection that nearby farms and homes depend on",
        "future_choice": "the choice between pursuing a handful of ambitious, fully naturalised restorations and spreading modest interventions across many more stretches of river",
        "scaleup_risk": "rolling out a single standard design across every river ignores the local hydrology that made any one restoration work in the first place",
    },
    {
        "subject": "responsible digital services",
        "actors": "product designers, data-protection officers, and community moderators",
        "origin": "a small team began adding opt-out defaults and usage-time reminders to an existing app after users complained about compulsive use",
        "daily_mechanism": "routine audits of default settings, algorithmic recommendations, and data-collection practices ahead of each product release",
        "funding_model": "a combination of subscription revenue, philanthropic grants, and a levy on advertising income",
        "benefit_primary": "users report spending less time on features designed to be habit-forming and gaining more control over what data is collected about them",
        "hidden_cost": "friction added to protect users also drives some of them toward less scrupulous competitors that impose no such limits",
        "evidence_tool": "usage logs, opt-out rates, and periodic user surveys on trust and perceived control",
        "evidence_dispute": "people who complete trust surveys are disproportionately those already satisfied with the service, which flatters the results",
        "governance_body": "an independent ethics board with the power to delay a feature launch",
        "tension": "commercial growth depends on engagement, while responsible design depends on limiting exactly the features that drive engagement",
        "future_choice": "the choice between adopting industry-wide standards that slow innovation and maintaining bespoke safeguards that are harder for users to compare across services",
        "scaleup_risk": "exporting one market's safeguards to another without adapting them can leave users less protected than a locally designed alternative would",
    },
    {
        "subject": "everyday wellbeing programmes",
        "actors": "community health workers, GPs, and trained peer mentors",
        "origin": "a local surgery began referring patients to a walking group instead of prescribing medication for mild anxiety, and the practice spread informally between clinics",
        "daily_mechanism": "short weekly sessions combining light exercise, peer conversation, and referral to other services when needed",
        "funding_model": "short-term health-board grants topped up by small charitable donations",
        "benefit_primary": "regular participants report fewer GP visits for stress-related complaints and improved sleep within a few months",
        "hidden_cost": "diverting patients away from clinical treatment can delay proper diagnosis for the minority whose symptoms need more than peer support",
        "evidence_tool": "referral records, patient-reported wellbeing scores, and follow-up calls at three and six months",
        "evidence_dispute": "patients referred to the programme are often already more motivated to improve their health than those who are not, which biases any comparison",
        "governance_body": "a joint committee of clinicians and patient representatives",
        "tension": "reaching people early, before symptoms become severe, depends on a low-key approach that resists the rigorous evaluation clinical treatment normally requires",
        "future_choice": "the choice between formalising the programme as a recognised clinical pathway and keeping it informal enough that GPs and patients continue to trust it",
        "scaleup_risk": "turning a trusted, informal referral habit into a standardised national programme risks losing the personal relationships that made patients take part in the first place",
    },
    {
        "subject": "regional transport networks",
        "actors": "route planners, bus operators, and passenger user-groups",
        "origin": "a handful of villages pooled resources to fund a single minibus route after the last commercial service was withdrawn",
        "daily_mechanism": "timetables built around school runs, market days, and hospital appointments rather than commuter peaks",
        "funding_model": "a blend of local-authority subsidy, fare revenue, and a rural-transport grant renewed annually",
        "benefit_primary": "older residents without cars have regained independent access to shops, clinics, and social visits",
        "hidden_cost": "subsidising a lightly used rural route diverts money away from busier corridors where it would carry more passengers per pound spent",
        "evidence_tool": "ticket-sales data, passenger counts by route and time of day, and annual satisfaction surveys",
        "evidence_dispute": "low passenger numbers on some routes look like failure in the data even though those routes serve people with no alternative at all",
        "governance_body": "a regional transport authority answerable to several local councils at once",
        "tension": "serving isolated communities well means running routes that will never be efficient by the standards used to judge the network as a whole",
        "future_choice": "the choice between cutting the least-used routes to protect the overall subsidy and preserving full coverage at growing cost per passenger",
        "scaleup_risk": "extending one district's successful timetable to a neighbouring district ignores differences in geography that made the original design work",
    },
    {
        "subject": "neighbourhood arts festivals",
        "actors": "local artists, shopkeepers, and a small team of volunteer organisers",
        "origin": "a group of resident artists closed off a side street for an afternoon of open studios, and the event grew by word of mouth in the years that followed",
        "daily_mechanism": "a weekend of staggered open studios, street performances, and stalls run almost entirely by unpaid volunteers",
        "funding_model": "a small council arts grant supplemented by stallholder fees and modest corporate sponsorship",
        "benefit_primary": "local businesses report a noticeable rise in footfall and sales during and immediately after the festival weekend",
        "hidden_cost": "growing visitor numbers have pushed up rents in the area, gradually displacing some of the artists whose studios first made the festival worth attending",
        "evidence_tool": "footfall counters, stallholder sales figures, and post-event surveys of residents and visitors",
        "evidence_dispute": "footfall counts do not distinguish festival visitors from people who would have been in the area anyway, which overstates the festival's specific impact",
        "governance_body": "a volunteer steering committee that reconstitutes itself informally each year",
        "tension": "growing the festival to attract more visitors changes the intimate, neighbourhood character that made it distinctive to begin with",
        "future_choice": "the choice between capping attendance to preserve the festival's original character and expanding it to secure more reliable long-term funding",
        "scaleup_risk": "professionalising the organisation to manage larger crowds risks squeezing out the volunteer spirit that residents value most about the event",
    },
    {
        "subject": "public observation projects",
        "actors": "professional scientists, trained volunteer observers, and local nature groups",
        "origin": "a university researcher recruited local birdwatchers to log sightings after funding for a dedicated fieldwork team fell through",
        "daily_mechanism": "standardised recording forms and a shared mobile app that volunteers use during regular, self-scheduled observation walks",
        "funding_model": "a research grant covering coordination costs, with volunteers contributing their time and equipment for free",
        "benefit_primary": "researchers have gathered a far larger and more geographically spread dataset than any funded fieldwork team could collect alone",
        "hidden_cost": "relying on unpaid volunteers to do work that would otherwise require paid scientific staff quietly shifts real costs onto people who are never compensated for them",
        "evidence_tool": "submitted observation records, cross-checks against expert verification, and periodic volunteer-retention statistics",
        "evidence_dispute": "sightings cluster near where volunteers happen to live and walk, so the data reflects human convenience as much as it reflects the species being studied",
        "governance_body": "a scientific advisory committee that sets recording standards for volunteers to follow",
        "tension": "recruiting enough volunteers to make the data useful requires simplifying the recording method, while scientific rigour depends on the very complexity that simplification removes",
        "future_choice": "the choice between broadening participation with an easier recording method and keeping a more demanding method that produces cleaner, more reliable data",
        "scaleup_risk": "opening the project to as many volunteers as possible without adequate training can flood the dataset with records too unreliable to use",
    },
    {
        "subject": "flexible workplace practices",
        "actors": "line managers, HR staff, and employees working non-standard hours",
        "origin": "a handful of staff quietly negotiated compressed hours with sympathetic managers before the arrangement was ever written into company policy",
        "daily_mechanism": "individually negotiated schedules, core hours for essential meetings, and remote-working days agreed team by team",
        "funding_model": "no separate budget beyond the cost of the software used to coordinate schedules across teams",
        "benefit_primary": "staff with caring responsibilities have stayed in their jobs at higher rates since flexible arrangements became widely available",
        "hidden_cost": "employees who work unusual hours are often overlooked for promotion because they are less visible to managers during conventional office hours",
        "evidence_tool": "retention statistics, staff-survey responses on autonomy, and productivity metrics tracked before and after the policy changed",
        "evidence_dispute": "productivity gains attributed to flexibility are hard to separate from the effect of hiring more experienced staff over the same period",
        "governance_body": "a joint management-employee working group that reviews the policy annually",
        "tension": "flexibility that benefits individual employees can undermine the shared availability that teamwork and client service depend on",
        "future_choice": "the choice between formalising flexible hours as an entitlement available to everyone and leaving them as a discretionary arrangement individual managers can withhold",
        "scaleup_risk": "imposing one flexible schedule across an entire organisation ignores the fact that different teams depend on very different patterns of overlap",
    },
    {
        "subject": "sustainable community kitchens",
        "actors": "volunteer cooks, food-waste collectors, and low-income households who rely on the meals",
        "origin": "a church hall began cooking surplus food donated by nearby supermarkets after a local charity noticed how much edible produce was going to waste",
        "daily_mechanism": "daily collection runs from supermarkets and wholesalers followed by same-day cooking and distribution of meals",
        "funding_model": "waste-reduction grants combined with a small charge for those who can afford to pay for meals",
        "benefit_primary": "households facing food insecurity have gained regular access to hot meals while measurably less edible food is sent to landfill",
        "hidden_cost": "depending on unpredictable donated surplus means the kitchen cannot guarantee a stable menu or quantity from one week to the next",
        "evidence_tool": "meals served, kilograms of food diverted from waste, and feedback forms completed by regular attendees",
        "evidence_dispute": "counting meals served does not show whether the same small group of people is returning repeatedly or whether the kitchen is reaching new households in need",
        "governance_body": "a management committee combining charity trustees and representatives of regular attendees",
        "tension": "relying on free surplus food keeps costs low but ties the kitchen's ability to help people to the unpredictable habits of nearby retailers",
        "future_choice": "the choice between buying some ingredients directly to guarantee consistent meals and remaining entirely dependent on donated surplus to keep costs down",
        "scaleup_risk": "expanding to serve far more people than the volunteer network can currently manage risks compromising food safety standards that smaller operations maintain more easily",
    },
    {
        "subject": "human-centred public spaces",
        "actors": "urban designers, local residents, and shopkeepers along the redesigned street",
        "origin": "residents temporarily closed a street to traffic for a single weekend trial, and the positive response persuaded the council to make the change permanent",
        "daily_mechanism": "wider pavements, reduced traffic speed, and seating installed where a road once carried through-traffic",
        "funding_model": "capital funding from a national active-travel scheme combined with ongoing council maintenance budgets",
        "benefit_primary": "pedestrian counts and time spent lingering in the redesigned space have both risen substantially since the changes were made",
        "hidden_cost": "restricting traffic on one street can simply push congestion onto neighbouring streets that were never redesigned to cope with it",
        "evidence_tool": "pedestrian and cyclist counts, shop-turnover figures, and resident surveys taken before and after the redesign",
        "evidence_dispute": "rising footfall could reflect a wider economic trend in the area rather than anything specific to the redesign itself",
        "governance_body": "a joint council and residents' panel that reviews complaints and monitors the redesign's effects",
        "tension": "prioritising pedestrians and cyclists on one street inevitably reduces convenience for the drivers and delivery vehicles that previously used it",
        "future_choice": "the choice between extending the redesign to a wider network of streets and consolidating the improvements already made to one street before expanding further",
        "scaleup_risk": "copying one street's design onto a busier or differently shaped street without adapting it can recreate the very congestion the original scheme was meant to relieve",
    },
    {
        "subject": "local archive preservation projects",
        "actors": "trained archivists, volunteer transcribers, and descendants of the families whose records are held",
        "origin": "a local historian began digitising a collection of parish registers stored in a damp church vestry before they deteriorated beyond recovery",
        "daily_mechanism": "a rolling schedule of cataloguing, careful digitisation, and climate-controlled storage for the most fragile items",
        "funding_model": "a heritage-lottery grant supplemented by donations from family-history researchers who use the collection",
        "benefit_primary": "records once accessible only by appointment at a single site can now be searched online by descendants scattered across the world",
        "hidden_cost": "digitising a collection can reduce the perceived urgency of preserving the fragile physical originals, which still require costly specialist storage",
        "evidence_tool": "download and search-query statistics, cataloguing-completion rates, and condition assessments of the physical originals",
        "evidence_dispute": "high download numbers for popular record sets say little about whether rarer, less-searched material is being preserved at all",
        "governance_body": "a heritage trust board that includes professional archivists and local-history society representatives",
        "tension": "making records widely accessible online depends on digitisation choices that a strict conservation standard would rule out on preservation grounds",
        "future_choice": "the choice between prioritising digitisation of the most-requested records and prioritising conservation of the most physically at-risk ones",
        "scaleup_risk": "rushing to digitise a much larger volume of material to meet demand can compromise the cataloguing accuracy that makes an archive usable rather than merely searchable",
    },
    {
        "subject": "multilingual public-information services",
        "actors": "professional translators, bilingual community liaison workers, and the residents who rely on translated information",
        "origin": "a local authority began translating emergency notices into the area's most common community languages after a public-health campaign failed to reach non-English speakers",
        "daily_mechanism": "a standing roster of translators and liaison workers who convert official notices into several languages before each is published",
        "funding_model": "a modest annual budget line shared across several council departments that all rely on the same translation team",
        "benefit_primary": "engagement with public services has risen noticeably among residents whose first language is not English since translations became routine",
        "hidden_cost": "resources devoted to a handful of widely spoken community languages leave speakers of rarer languages still effectively excluded from official information",
        "evidence_tool": "service-uptake figures broken down by language, translation-request volumes, and complaints about missing translations",
        "evidence_dispute": "rising uptake among translated-language speakers could reflect a wider outreach campaign running at the same time rather than translation alone",
        "governance_body": "a communications oversight panel that decides which languages receive priority translation",
        "tension": "responding quickly to urgent public announcements is hard to reconcile with the careful, unhurried translation that avoids dangerous misunderstandings",
        "future_choice": "the choice between expanding the number of languages covered and investing instead in faster turnaround for the languages already covered",
        "scaleup_risk": "relying on machine translation to cover more languages more cheaply risks introducing exactly the misunderstandings that human translation was introduced to prevent",
    },
    {
        "subject": "small-business resilience plans",
        "actors": "business advisers, chamber-of-commerce staff, and independent shop owners",
        "origin": "a chamber of commerce began running free workshops on cash-flow planning after a wave of closures during a difficult trading period",
        "daily_mechanism": "one-to-one advice sessions, peer-mentoring pairs, and a shared emergency fund that participating businesses can borrow from briefly",
        "funding_model": "a local-authority economic-development grant matched by small membership contributions from participating businesses",
        "benefit_primary": "participating businesses have survived unexpected disruptions, such as a sudden rent rise or a burst pipe, at noticeably higher rates than non-participants",
        "hidden_cost": "time spent attending workshops and mentoring sessions is time the smallest businesses, often just one or two people, cannot easily spare",
        "evidence_tool": "business survival rates, loan-repayment records, and post-crisis surveys of participating owners",
        "evidence_dispute": "businesses that choose to join a resilience programme may simply be more cautious and better managed to begin with, regardless of the programme's own effect",
        "governance_body": "a steering group of chamber staff and elected representatives of the participating businesses",
        "tension": "building resilience takes time and planning that struggling businesses, who need help most urgently, are the least able to spare",
        "future_choice": "the choice between targeting support at the most vulnerable businesses and opening the programme to any business that wants to join",
        "scaleup_risk": "extending the shared emergency fund to many more businesses without increasing its size risks leaving it unable to help anyone when several businesses need it at once",
    },
    {
        "subject": "climate-aware farming methods",
        "actors": "farmers, agronomists, and a regional farming cooperative",
        "origin": "a small group of farmers began trialling cover crops and reduced tillage after a series of unusually dry seasons damaged conventional yields",
        "daily_mechanism": "seasonal rotation of cover crops, reduced ploughing, and closer monitoring of soil moisture than conventional methods require",
        "funding_model": "a government environmental-payment scheme combined with cooperative bulk-purchasing of seed and equipment",
        "benefit_primary": "soil organic matter and water retention have improved measurably on farms that adopted the new methods for several consecutive seasons",
        "hidden_cost": "yields can dip in the first few transition years, a period many farmers cannot financially survive without the environmental payments bridging the gap",
        "evidence_tool": "soil-sample test results, yield records over several seasons, and farmer-reported input costs",
        "evidence_dispute": "unusually favourable rainfall in the years since the trial began makes it hard to separate the method's own effect from simple good weather",
        "governance_body": "a cooperative board of participating farmers advised by an agricultural extension officer",
        "tension": "practices that protect long-term soil health can reduce short-term yield at exactly the moment when farmers most need reliable income",
        "future_choice": "the choice between making the new methods a condition of continued environmental payments and leaving adoption voluntary for now",
        "scaleup_risk": "mandating one set of practices across very different soil types and climates ignores the local trial-and-error that made the original farms succeed",
    },
    {
        "subject": "local energy-saving initiatives",
        "actors": "energy advisers, housing-association staff, and residents whose homes were retrofitted",
        "origin": "a housing association began offering free loft insulation to tenants after noticing how much of its residents' income went on winter heating bills",
        "daily_mechanism": "door-to-door energy audits followed by scheduled retrofit work such as insulation, draught-proofing, and smart heating controls",
        "funding_model": "a national energy-efficiency grant topped up by the housing association's own maintenance budget",
        "benefit_primary": "retrofitted households have reported noticeably lower heating bills and warmer homes during the following winter",
        "hidden_cost": "retrofit work often disrupts a household for days at a time, a cost that falls hardest on residents who cannot easily take time off work to be present",
        "evidence_tool": "metered energy-use data before and after retrofit, tenant-reported comfort surveys, and contractor completion records",
        "evidence_dispute": "lower bills after a retrofit could partly reflect a milder winter rather than the retrofit itself, since the two are hard to disentangle from meter readings alone",
        "governance_body": "a joint panel of housing-association managers and tenant representatives",
        "tension": "the households that would benefit most from a retrofit are often the hardest to reach, since they are the ones least able to take time off to let contractors in",
        "future_choice": "the choice between prioritising the least energy-efficient homes first and working street by street to keep contractor costs down",
        "scaleup_risk": "rushing retrofit work to hit an annual target can leave installations poorly finished in ways that only become apparent after the contractors have left",
    },
    {
        "subject": "coastal monitoring programmes",
        "actors": "marine biologists, fishing-boat crews, and volunteer beach surveyors",
        "origin": "a marine research station began paying local fishing crews a small fee to log water temperature and catch data on their regular trips",
        "daily_mechanism": "routine measurements taken during fishing trips and monthly beach transects walked by trained volunteer surveyors",
        "funding_model": "a research-council grant supplemented by a modest per-trip payment to participating fishing crews",
        "benefit_primary": "scientists have detected shifts in fish distribution and water temperature far earlier than a small research team could have observed alone",
        "hidden_cost": "relying on fishing crews for data creates a quiet conflict of interest when the same data might eventually justify restrictions on their own fishing grounds",
        "evidence_tool": "logged catch and temperature records, beach-litter counts, and periodic laboratory verification of a sample of the volunteer data",
        "evidence_dispute": "crews fish where fish are most likely to be found, so the data reflects good fishing spots as much as it reflects the wider health of the coastline",
        "governance_body": "an advisory board of marine scientists, fishing-industry representatives, and coastal-authority officials",
        "tension": "the people best placed to gather frequent coastal data are often the same people whose livelihoods the resulting findings could eventually restrict",
        "future_choice": "the choice between expanding paid data collection to more fishing crews and investing instead in independent monitoring equipment that removes any conflict of interest",
        "scaleup_risk": "adding many more volunteer surveyors without expanding the laboratory capacity to verify their data risks producing a much larger dataset that is no more trustworthy than before",
    },
    {
        "subject": "attention and learning support programmes",
        "actors": "school counsellors, classroom teachers, and the pupils receiving support",
        "origin": "a secondary school introduced short daily focus exercises for pupils who found it hard to concentrate, after noticing a marked rise in reported difficulty attending to schoolwork",
        "daily_mechanism": "brief structured exercises woven into the start of lessons and reviewed with a counsellor once a week",
        "funding_model": "a small allocation from the school's existing pastoral-care budget rather than any dedicated new funding",
        "benefit_primary": "participating pupils have shown improved sustained attention and fewer reported difficulties completing homework within a single term",
        "hidden_cost": "time spent on focus exercises is time taken away from the subject teaching that pupils and parents ultimately expect the timetable to prioritise",
        "evidence_tool": "teacher-rated attention scores, homework-completion records, and pupil self-report questionnaires",
        "evidence_dispute": "teachers who know which pupils are receiving the intervention may unconsciously rate their attention more favourably than they would otherwise",
        "governance_body": "a pastoral-care team that includes senior teachers and an educational psychologist",
        "tension": "addressing attention difficulties properly takes sustained, individualised time that a normal class timetable was never designed to provide",
        "future_choice": "the choice between offering the programme to every pupil as standard practice and reserving it for those already identified as struggling",
        "scaleup_risk": "delivering the exercises to a whole year group at once, rather than in small groups, risks losing the individual attention that made the original trial effective",
    },
    {
        "subject": "adaptive-reuse building projects",
        "actors": "conservation architects, structural engineers, and the tenants who eventually occupy the converted building",
        "origin": "a disused mill was due for demolition until a local developer proposed converting it into workspace instead of clearing the site entirely",
        "daily_mechanism": "phased construction that retains the original structure while inserting new services, insulation, and internal partitions",
        "funding_model": "heritage tax incentives combined with private investment secured against the eventual rental income",
        "benefit_primary": "converting the building has used markedly less embodied carbon than demolishing it and constructing an equivalent new building would have",
        "hidden_cost": "retaining an old structure often means living with awkward floor plans and lower ceiling heights that a purpose-built alternative would have avoided",
        "evidence_tool": "carbon-audit calculations, post-occupancy energy readings, and tenant surveys on comfort and layout",
        "evidence_dispute": "carbon savings calculated at the point of conversion do not account for the building's ongoing energy performance, which can be worse than a new, better-insulated building over time",
        "governance_body": "a heritage and planning panel that must approve any structural changes to the retained building",
        "tension": "preserving the historic character that justified conversion in the first place limits exactly the structural changes that would make the building most energy-efficient",
        "future_choice": "the choice between pursuing further heritage conversions on similar sites and reserving conversion for buildings of genuinely exceptional architectural or historical value",
        "scaleup_risk": "treating every old building as suitable for conversion, regardless of its condition, can produce projects that cost more and perform worse than a straightforward new building",
    },
    {
        "subject": "community information networks",
        "actors": "citizen reporters, a small paid editorial team, and residents who rely on local coverage",
        "origin": "a group of residents started a neighbourhood newsletter after the last local newspaper closed and stopped covering council meetings altogether",
        "daily_mechanism": "volunteer reporters filing short updates that a small paid editorial team checks and publishes across a website and social channels",
        "funding_model": "reader donations combined with a small grant supporting local-journalism initiatives",
        "benefit_primary": "residents report feeling noticeably better informed about council decisions and local events than they did when no local coverage existed",
        "hidden_cost": "relying on volunteer reporters means coverage depends heavily on whoever happens to be available, which leaves some parts of the community consistently under-reported",
        "evidence_tool": "readership figures, story counts by neighbourhood, and reader surveys on trust and perceived usefulness",
        "evidence_dispute": "readership figures are highest for the most sensational stories, which says little about whether residents are actually better informed on routine local matters",
        "governance_body": "an editorial board of volunteer reporters and community representatives that sets coverage priorities",
        "tension": "covering routine council business fairly requires more resources than the network has, while the volunteer effort available is drawn instead to whatever story is currently attracting attention",
        "future_choice": "the choice between hiring more paid staff, funded by asking readers to pay for access, and remaining free but reliant on unpredictable volunteer effort",
        "scaleup_risk": "expanding coverage to neighbouring areas without recruiting local reporters there risks producing coverage written by outsiders about places they do not actually know",
    },
    {
        "subject": "urban wildlife corridors",
        "actors": "council ecologists, residents with gardens along the route, and a local wildlife trust",
        "origin": "a wildlife trust persuaded several neighbouring households to leave connected sections of their gardens unmown, and the informal chain of habitat grew from there",
        "daily_mechanism": "seasonal planting, hedgerow maintenance, and monitoring of the connected gardens and verges that make up the corridor",
        "funding_model": "a small council biodiversity grant combined with plants and labour donated by participating households",
        "benefit_primary": "recorded sightings of hedgehogs and pollinating insects have risen noticeably along the corridor since it was established",
        "hidden_cost": "a corridor threading through private gardens depends entirely on residents continuing to maintain their section, and any household that stops or moves away leaves a gap that can cut the route in two",
        "evidence_tool": "resident-logged wildlife sightings, camera-trap footage at key points along the corridor, and annual habitat-condition surveys",
        "evidence_dispute": "rising sightings could reflect more residents simply looking for wildlife and reporting it, rather than any real increase in the animals themselves",
        "governance_body": "a wildlife trust coordinator working with an informal residents' committee along the corridor",
        "tension": "a corridor that depends on voluntary cooperation between private households is inherently fragile in a way that land under single public ownership would not be",
        "future_choice": "the choice between negotiating formal, lasting agreements with each participating household and continuing to rely on informal goodwill that costs nothing but cannot be guaranteed",
        "scaleup_risk": "extending the corridor into areas with less community engagement risks creating gaps that undermine the connectivity the whole project depends on",
    },
]


ACTORS_SHORT = "those involved"
GOVERNANCE_SHORT = "this body"
FUNDING_SHORT = "this funding base"
EVIDENCE_TOOL_SHORT = "these same records"


def cap(s):
    return s[0].upper() + s[1:]


def derive(f):
    d = dict(f)
    d["Subject_cap"] = cap(f["subject"])
    d["Origin_cap"] = cap(f["origin"])
    d["Tension_cap"] = cap(f["tension"])
    d["Funding_model_cap"] = cap(f["funding_model"])
    d["Governance_body_cap"] = cap(f["governance_body"])
    d["actors_short"] = ACTORS_SHORT
    d["governance_body_short"] = GOVERNANCE_SHORT
    d["funding_model_short"] = FUNDING_SHORT
    d["evidence_tool_short"] = EVIDENCE_TOOL_SHORT
    return d


def angle_origins(f):
    f = derive(f)
    return [
        (
            "{Subject_cap} did not emerge from a single decision so much as accrete over time. "
            "{Origin_cap}, and what began as a modest, largely improvised response has since acquired the trappings "
            "of a permanent institution — a name, a governance structure, and a constituency that expects it to "
            "continue. The people most associated with the initiative, {actors}, were not originally recruited so "
            "much as they simply turned up, and the roles they now occupy were negotiated informally long before "
            "any job description existed. This pattern is not unusual: durable community institutions are rarely "
            "designed in advance so much as recognised, after the fact, as having become necessary."
        ).format(**f),
        (
            "Day to day, the initiative runs on {daily_mechanism}, a pattern that looks casual from outside but "
            "conceals a good deal of coordination. Resources are stretched by {funding_model}, which means that "
            "continuity depends less on any single grant than on the willingness of {actors_short} to absorb "
            "uncertainty that better-funded institutions would not tolerate. The operating rhythm reflects a "
            "deliberate, if rarely stated, trade-off: {tension}. Visitors sometimes mistake the resulting "
            "informality for a lack of rigour, when it is closer to a considered response to conditions that a "
            "more rigid structure would struggle to survive."
        ).format(**f),
        (
            "What can be said with confidence rests on {evidence_tool}, supplemented by the accumulated, largely "
            "undocumented experience of {actors_short}. That evidence is suggestive rather than conclusive: "
            "{evidence_dispute}. Even so, dismissing it as merely anecdotal would understate its value — those "
            "closest to daily operation notice shifts in demand well before any formal indicator registers them. "
            "The honest position is that the initiative is better understood than it is measured, and that gap "
            "between understanding and measurement recurs throughout small-scale public provision generally."
        ).format(**f),
        (
            "The most persistent difficulty is not any single crisis but the slow accumulation of strain that "
            "{funding_model_short} makes almost inevitable. Because resources are so narrowly stretched, minor "
            "setbacks that a larger institution could absorb instead compound, and {actors_short} are left "
            "improvising solutions that were never meant to be permanent. {Tension_cap}, and it sharpens under "
            "pressure: choices that seemed reasonable when resources were adequate become contested once they are "
            "not. None of this is unique to the initiative, but its effects are felt earlier and more acutely than "
            "in institutions with deeper reserves."
        ).format(**f),
        (
            "Looking ahead, those responsible face {future_choice}, a decision made harder by the fact that "
            "{scaleup_risk}. There is no formula that resolves this cleanly; whichever path is chosen will trade "
            "one kind of vulnerability for another. What seems clear is that {actors_short} would rather adapt the "
            "existing model incrementally than replace it wholesale, if only because so much of what makes the "
            "initiative work is informal knowledge that a redesign could easily discard."
        ).format(**f),
    ]


def angle_benefits(f):
    f = derive(f)
    return [
        (
            "The initiative was introduced with a fairly narrow promise: {benefit_primary}. That promise explains "
            "why {actors} were willing to invest time in something with no guaranteed return, and it still "
            "supplies the justification used whenever funding comes under review. What has proved harder to "
            "anticipate is how much of the initiative's real value now lies outside that original promise, in "
            "effects nobody quite planned for and few can take credit for."
        ).format(**f),
        (
            "The day-to-day mechanics — {daily_mechanism} — were designed around delivering that original promise "
            "as efficiently as possible. In practice, though, this is not the whole story: {hidden_cost}, and the "
            "effect only became visible once the initiative had been running long enough to generate a track "
            "record. {Tension_cap}, and optimising for the stated benefit tends to crowd out the conditions that "
            "made the initiative worth having in the first place."
        ).format(**f),
        (
            "Testimony from {actors_short}, together with {evidence_tool}, confirms that {benefit_primary}, a "
            "pattern too consistent to be coincidental. The same sources, however, reveal a less flattering "
            "picture: {evidence_dispute}, so the recorded benefits are almost certainly an overstatement of what a "
            "typical participant experiences. Whether this matters depends on what the evidence is being used "
            "for — as a reason to continue, the imprecision is tolerable; as a basis for expansion, it is not."
        ).format(**f),
        (
            "The costs that were not advertised at the outset are now the hardest to manage, precisely because "
            "{hidden_cost}. {Funding_model_cap} leaves little room to address this without displacing something "
            "else, forcing {actors_short} into trade-offs that were never made explicit to the people who rely on "
            "the initiative. Naming the cost openly would arguably help, but doing so risks undermining the "
            "confidence on which continued support depends."
        ).format(**f),
        (
            "Any credible plan now has to weigh {future_choice} against the likelihood that {scaleup_risk}. The "
            "temptation is to keep emphasising the original promise while quietly managing the less visible costs; "
            "a more honest approach would put both sides of the ledger in front of {actors_short} and the wider "
            "public, even at the risk of complicating a message that has so far worked because it was simple."
        ).format(**f),
    ]


def angle_measurement(f):
    f = derive(f)
    return [
        (
            "Assessing the initiative is complicated by the fact that it was never built with evaluation in mind. "
            "{Origin_cap}, and record-keeping was added later, as an afterthought rather than a design principle. "
            "Consequently, the earliest years are documented mainly through the recollections of {actors}, which "
            "are valuable but not verifiable in the way a formal dataset would be. Any claim about the "
            "initiative's overall trajectory has to be read against this uneven evidentiary base."
        ).format(**f),
        (
            "Current practice draws on {evidence_tool}, generated as a by-product of {daily_mechanism} rather than "
            "through any purpose-built monitoring system. This has the advantage of low cost and minimal "
            "disruption to {actors_short}, but the disadvantage that {evidence_dispute}. Decision-makers who treat "
            "these figures as precise risk building policy on a foundation that was never meant to bear that "
            "weight."
        ).format(**f),
        (
            "The strongest evidence concerns the initiative's central claim, where {evidence_tool_short} converge "
            "with the lived impressions of {actors_short} closely enough to inspire reasonable confidence that "
            "{benefit_primary}. Weaker evidence surrounds one recurring cost — {hidden_cost} — which the same "
            "instruments rarely capture, so it tends to be underrepresented in any summary of outcomes. "
            "{Tension_cap}, and this is, in effect, a difference in how well each side of the initiative is "
            "measured, not necessarily in how much each side matters."
        ).format(**f),
        (
            "{Governance_body_cap} must decide how much weight to place on evidence that {evidence_dispute}, a "
            "judgement call with no neutral answer. Overstating confidence in the numbers invites decisions that "
            "later prove unjustified; treating all figures as unreliable, meanwhile, hands the argument to "
            "whoever is most persuasive rather than whoever is most correct. Both errors have occurred at "
            "different points in the initiative's history."
        ).format(**f),
        (
            "Improving the evidence base would mean investing in measurement that the initiative has so far "
            "managed without, which raises the familiar objection that {scaleup_risk}. A more modest step — "
            "auditing existing records for the specific gap identified above, namely that {evidence_dispute} — "
            "would cost less and could plausibly be completed by {governance_body_short} within a single funding "
            "cycle, offering a first, testable improvement rather than a wholesale overhaul."
        ).format(**f),
    ]


def angle_future(f):
    f = derive(f)
    return [
        (
            "Decisions about the initiative were, from the start, made informally. {Origin_cap}, and no clear "
            "line of accountability was ever drawn around who had the authority to change course. That "
            "arrangement suited an initiative with modest ambitions, but it sits awkwardly with the scale the "
            "initiative has since reached, where choices now have consequences for people well beyond {actors}."
        ).format(**f),
        (
            "{Governance_body_cap} now oversees the initiative, though the relationship between this body and the "
            "day-to-day judgement exercised by {actors_short} through {daily_mechanism} is not always clearly "
            "specified. In effect, authority is shared without being formally divided. {Tension_cap}, and the "
            "arrangement works well enough while priorities align but becomes contentious the moment that tension "
            "turns into an open disagreement rather than a background assumption."
        ).format(**f),
        (
            "When {governance_body_short} has had to make contested decisions, the evidence offered in support — "
            "largely {evidence_tool} — has proved persuasive to some and inadequate to others, partly because "
            "{evidence_dispute}. This has made governance feel, at times, less like a process of weighing evidence "
            "and more like a negotiation between people who already knew which conclusion they wanted the evidence "
            "to support."
        ).format(**f),
        (
            "The central governance dilemma is {future_choice}, and it is complicated by the fact that "
            "{scaleup_risk}. Whichever way {governance_body_short} leans, some part of the initiative's original "
            "character will be sacrificed, and {actors_short} are unlikely to agree in advance about which losses "
            "are acceptable. Deferring the decision has its own cost, since problems that go unaddressed rarely "
            "stay the same size: {hidden_cost}."
        ).format(**f),
        (
            "What happens next will depend less on new evidence than on which value {governance_body_short} "
            "chooses to prioritise when trade-offs resurface. A defensible process would make that choice "
            "explicit — stating plainly that {future_choice} has been settled one way rather than the other, and "
            "why — instead of allowing the outcome to be decided by default through funding decisions that nobody "
            "frames as a governance choice at all."
        ).format(**f),
    ]


ANGLE_FUNCS = {
    "origins_and_daily_operation": angle_origins,
    "benefits_and_unexpected_costs": angle_benefits,
    "measurement_and_evidence": angle_measurement,
    "future_choices_and_governance": angle_future,
}


def main():
    data_dir = os.path.join("data", "C2")
    files = sorted(glob.glob(os.path.join(data_dir, "*.json")))
    assert len(files) == 80, "expected 80 C2 files, found {}".format(len(files))

    updated = 0
    for group_index, group_start in enumerate(range(0, 80, 4)):
        domain = DOMAINS[group_index]
        group_files = files[group_start:group_start + 4]
        for filepath in group_files:
            angle = None
            for a in ANGLE_ORDER:
                if "_{}_in_".format(a) in os.path.basename(filepath):
                    angle = a
                    break
            if angle is None:
                raise ValueError("Could not determine angle for {}".format(filepath))

            with open(filepath, encoding="utf-8") as fh:
                doc = json.load(fh)

            paragraphs = ANGLE_FUNCS[angle](domain)

            sections = []
            full_text_parts = []
            for i, heading in enumerate(HEADINGS):
                text = paragraphs[i]
                sections.append({"paragraph": i + 1, "heading": heading, "text": text})
                full_text_parts.append("Paragraph {} — {}\n{}".format(i + 1, heading, text))

            doc["passage"]["sections"] = sections
            doc["passage"]["full_text"] = "\n\n".join(full_text_parts)

            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(doc, fh, indent=2, ensure_ascii=False)

            updated += 1

    print("Updated {} C2 passages.".format(updated))


if __name__ == "__main__":
    main()
