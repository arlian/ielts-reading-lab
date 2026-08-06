#!/usr/bin/env python3
"""
Regenerate B2 passage text with substantive, topic-specific, B2-register content.

Only passage.sections[].text and passage.full_text are rewritten. Everything
else in each file (questions, answer_key, metadata, topic info) is preserved.

Register differs deliberately from the C2 rewrite: shorter sentences, less
subordination, and concrete grounding (dates, places, budgets, statistics) in
line with WRITING_GUIDE.md. The topical fields are shared with
regenerate_c2_passages.py so that a topic reads consistently across levels;
the numeric and place detail below is specific to B2.

The extra file B2_321 is a hand-written passage and is left untouched.
"""

import json
import glob
import os

from regenerate_c2_passages import DOMAINS as BASE_DOMAINS, HEADINGS, ANGLE_ORDER, cap

# Concrete grounding for each domain, in the same order as BASE_DOMAINS.
# All names, figures and organisations are synthetic practice material.
CONTEXT = [
    {  # community learning centres
        "place": "the English city of Leicester",
        "start_year": "2011",
        "founder": "a retired secondary-school teacher, Margaret Ellis,",
        "origin_event": "began running free evening tutoring in a borrowed shop unit",
        "early_scale": "opened two evenings a week and taught eleven students",
        "current_scale": "about 480 adult learners a year across three sites",
        "recent_year": "2024",
        "annual_budget": "£210,000",
        "benefit_stat": "in 2024, 68% of learners who finished a course said they felt more confident using online public services, compared with 41% at enrolment",
        "cost_stat": "roughly a third of those who enrol stop attending before their course ends",
        "evidence_stat": "follow-up interviews six months later reach only about half of former learners",
    },
    {  # river restoration projects
        "place": "West Yorkshire in northern England",
        "start_year": "2009",
        "founder": "a local angling club",
        "origin_event": "campaigned for the removal of a derelict mill weir on the River Aire",
        "early_scale": "covered a single three-kilometre stretch of river",
        "current_scale": "27 kilometres of restored channel managed by a catchment partnership",
        "recent_year": "2023",
        "annual_budget": "£640,000",
        "benefit_stat": "surveys recorded a 40% rise in trout numbers in the restored stretches between 2015 and 2023",
        "cost_stat": "two downstream villages reported higher flood peaks after the third weir was removed",
        "evidence_stat": "fish counts are taken at only nine fixed points along those 27 kilometres",
    },
    {  # responsible digital services
        "place": "Helsinki in Finland",
        "start_year": "2018",
        "founder": "a four-person product team at a mid-sized software company",
        "origin_event": "added opt-out defaults and usage-time reminders to an app used by 300,000 people",
        "early_scale": "changed three settings in a single product",
        "current_scale": "a review applied to every release across six products",
        "recent_year": "2024",
        "annual_budget": "€480,000",
        "benefit_stat": "average daily session length fell by 22% in the year after the reminders were introduced, while monthly cancellations rose by only 3%",
        "cost_stat": "about 9% of users who left named the new limits as their reason for moving to a rival service",
        "evidence_stat": "fewer than one user in twenty completes the annual trust survey",
    },
    {  # everyday wellbeing programmes
        "place": "the Scottish city of Dundee",
        "start_year": "2016",
        "founder": "a single GP surgery",
        "origin_event": "began referring patients with mild anxiety to a weekly walking group instead of prescribing medication",
        "early_scale": "took referrals from four doctors at one practice",
        "current_scale": "about 1,200 referrals a year from eleven practices",
        "recent_year": "2024",
        "annual_budget": "£95,000",
        "benefit_stat": "participants recorded 19% fewer GP appointments for stress-related complaints in the six months after joining",
        "cost_stat": "for about 7% of those referred, a condition needing clinical treatment was identified later than it would otherwise have been",
        "evidence_stat": "wellbeing scores are collected at three and six months, but only 61% of participants complete the second questionnaire",
    },
    {  # regional transport networks
        "place": "rural Powys in mid-Wales",
        "start_year": "2013",
        "founder": "four village councils",
        "origin_event": "pooled their budgets to fund one minibus after the last commercial bus service was withdrawn",
        "early_scale": "ran a single route three days a week",
        "current_scale": "six routes carrying about 60,000 passenger journeys a year",
        "recent_year": "2024",
        "annual_budget": "£520,000",
        "benefit_stat": "surveys found that 72% of regular passengers are over 65 and have no access to a car",
        "cost_stat": "the least-used route costs £11 in subsidy for every passenger journey, against £2.40 on the busiest",
        "evidence_stat": "on four of the six routes, passenger numbers are counted by drivers rather than by ticket machines",
    },
    {  # neighbourhood arts festivals
        "place": "a central district of Porto",
        "start_year": "2012",
        "founder": "a group of eleven resident artists",
        "origin_event": "closed one side street for an afternoon of open studios",
        "early_scale": "lasted a single afternoon and drew perhaps 300 visitors",
        "current_scale": "a three-day festival with 40 open studios and around 25,000 visitors",
        "recent_year": "2024",
        "annual_budget": "€180,000",
        "benefit_stat": "shops along the festival route reported a 31% rise in takings during the 2024 event",
        "cost_stat": "studio rents in the district have risen by 45% since 2015, and nine of the founding artists have moved away",
        "evidence_stat": "the footfall counters cannot separate festival visitors from residents going about their usual business",
    },
    {  # public observation projects
        "place": "the Otago region of New Zealand",
        "start_year": "2015",
        "founder": "a university researcher",
        "origin_event": "recruited local birdwatchers to log sightings after funding for a paid fieldwork team fell through",
        "early_scale": "relied on 30 volunteers recording in one valley",
        "current_scale": "900 volunteers submitting about 140,000 records a year",
        "recent_year": "2024",
        "annual_budget": "NZ$210,000",
        "benefit_stat": "the volunteer dataset now covers fourteen times more ground than the original funded survey did",
        "cost_stat": "expert checks on a 5% sample found errors in 12% of the records examined",
        "evidence_stat": "almost two-thirds of all sightings come from within five kilometres of a main road",
    },
    {  # flexible workplace practices
        "place": "Rotterdam in the Netherlands",
        "start_year": "2017",
        "founder": "a handful of staff at a 600-person engineering firm",
        "origin_event": "negotiated compressed hours privately with sympathetic managers",
        "early_scale": "involved nine employees in one department",
        "current_scale": "formal arrangements covering 610 staff across the company",
        "recent_year": "2024",
        "annual_budget": "€40,000",
        "funding_model": "a small line in the human-resources budget that covers the scheduling software",
        "benefit_stat": "retention among staff with caring responsibilities rose from 71% in 2017 to 88% in 2024",
        "cost_stat": "employees on non-standard hours made up 34% of the workforce but received only 12% of internal promotions",
        "evidence_stat": "productivity was measured before and after the change, but the firm also hired 80 experienced engineers in the same period",
    },
    {  # sustainable community kitchens
        "place": "Bristol in south-west England",
        "start_year": "2014",
        "founder": "a volunteer group based in a church hall",
        "origin_event": "began cooking surplus produce donated by two nearby supermarkets",
        "early_scale": "served about 40 meals a week",
        "current_scale": "roughly 900 meals a week and 32 tonnes of food diverted from waste each year",
        "recent_year": "2024",
        "annual_budget": "£145,000",
        "benefit_stat": "a 2024 survey found that 84% of regular attendees called the kitchen was their main source of a hot meal on the days it opens",
        "cost_stat": "donated quantities vary by as much as 60% from one week to the next, so the menu cannot be planned in advance",
        "evidence_stat": "the kitchen counts meals served but not individual visitors, so repeat attendance is invisible in the figures",
    },
    {  # human-centred public spaces
        "place": "a northern district of Melbourne",
        "start_year": "2019",
        "founder": "a residents' association",
        "origin_event": "persuaded the council to close one shopping street to traffic for a single weekend trial",
        "early_scale": "covered 200 metres of one street for two days",
        "current_scale": "a permanent redesign of 1.2 kilometres of street",
        "recent_year": "2024",
        "annual_budget": "A$310,000",
        "benefit_stat": "pedestrian counts rose by 54%, and the average time people spent in the street more than doubled",
        "cost_stat": "traffic on two neighbouring residential streets increased by about 18%",
        "evidence_stat": "shop turnover rose by 12%, but the wider district saw a 7% rise over the same period",
    },
    {  # local archive preservation projects
        "place": "the Irish city of Galway",
        "start_year": "2010",
        "founder": "a local historian",
        "origin_event": "began photographing parish registers stored in a damp church vestry",
        "early_scale": "covered one parish and about 4,000 pages",
        "current_scale": "220,000 digitised pages searched roughly 60,000 times a year",
        "recent_year": "2024",
        "annual_budget": "€120,000",
        "benefit_stat": "records once available only by appointment are now consulted by researchers in 38 countries",
        "cost_stat": "only 15% of the original documents have been moved into climate-controlled storage, and conservation funding has fallen since digitisation began",
        "evidence_stat": "download figures are dominated by 200 popular record sets and say nothing about the rest of the collection",
    },
    {  # multilingual public-information services
        "place": "the Swedish city of Malmö",
        "start_year": "2015",
        "founder": "the city council's communications team",
        "origin_event": "began translating emergency notices after a public-health campaign failed to reach residents who spoke little Swedish",
        "early_scale": "translated urgent notices into three languages",
        "current_scale": "routine translation into seven languages for five council departments",
        "recent_year": "2024",
        "annual_budget": "4.2 million kronor",
        "benefit_stat": "uptake of council services among residents whose first language is not Swedish rose by 26% between 2016 and 2023",
        "cost_stat": "speakers of the twenty next most common languages, about 6% of residents, still receive nothing in their own language",
        "evidence_stat": "uptake rose during the same years as a separate outreach campaign, so the two effects cannot be separated",
    },
    {  # small-business resilience plans
        "place": "Sheffield in northern England",
        "start_year": "2016",
        "founder": "the local chamber of commerce",
        "origin_event": "started free cash-flow workshops after 40 independent shops closed in a single year",
        "early_scale": "enrolled 18 businesses",
        "current_scale": "240 member businesses and a shared emergency fund of £300,000",
        "recent_year": "2024",
        "annual_budget": "£175,000",
        "benefit_stat": "some 84% of participating businesses survived a major disruption between 2020 and 2024, against 66% of comparable non-members",
        "cost_stat": "businesses with fewer than three employees attend only about half the sessions they sign up for",
        "evidence_stat": "the businesses that choose to join tend to be more cautious than average, which flatters the comparison",
    },
    {  # climate-aware farming methods
        "place": "Jutland in western Denmark",
        "start_year": "2014",
        "founder": "twelve farmers",
        "origin_event": "began trialling cover crops and reduced ploughing after three unusually dry summers cut their yields",
        "early_scale": "covered 400 hectares",
        "current_scale": "an 86-farm cooperative working 21,000 hectares",
        "recent_year": "2024",
        "annual_budget": "9 million kroner",
        "benefit_stat": "soil organic matter rose from 2.1% to 2.9% on the earliest farms, and water retention improved with it",
        "cost_stat": "yields fell by an average of 8% during the first two years of the change",
        "evidence_stat": "rainfall since 2016 has been above the long-term average, which makes the method's own effect hard to isolate",
    },
    {  # local energy-saving initiatives
        "place": "Sunderland in north-east England",
        "start_year": "2015",
        "founder": "a housing association",
        "origin_event": "offered free loft insulation to tenants after finding that some households spent a fifth of their income on heating",
        "early_scale": "insulated 60 homes on one estate",
        "current_scale": "1,800 homes retrofitted",
        "recent_year": "2024",
        "annual_budget": "£2.1 million",
        "benefit_stat": "metered gas use in retrofitted homes fell by 23% on average in the following winter",
        "cost_stat": "the work leaves a household disrupted for three to five days, and 28% of eligible tenants declined for that reason",
        "evidence_stat": "the winter after the largest phase of work was 1.4°C milder than the one before it",
    },
    {  # coastal monitoring programmes
        "place": "Galicia in north-west Spain",
        "start_year": "2012",
        "founder": "a marine research station",
        "origin_event": "paid local fishing crews a small fee to log water temperature and catch data on their usual trips",
        "early_scale": "involved six boats from one harbour",
        "current_scale": "30 crews and a team of volunteer surveyors submitting about 45,000 readings a year",
        "recent_year": "2024",
        "annual_budget": "€390,000",
        "benefit_stat": "the data revealed a northward shift in two commercial fish species four years before national surveys recorded it",
        "cost_stat": "the same data has since been cited in proposals to restrict fishing in three areas where the participating crews work",
        "evidence_stat": "laboratory checks cover only 4% of the readings submitted",
    },
    {  # attention and learning support programmes
        "place": "Christchurch in New Zealand",
        "start_year": "2018",
        "founder": "the counselling team at one secondary school",
        "origin_event": "introduced ten-minute focus exercises at the start of lessons for pupils who struggled to concentrate",
        "early_scale": "involved one year group of 90 pupils",
        "current_scale": "all 1,100 pupils, with weekly small-group review for about 140 of them",
        "recent_year": "2024",
        "annual_budget": "NZ$60,000",
        "benefit_stat": "homework completion among participating pupils rose from 62% to 79% within a single term",
        "cost_stat": "the exercises take about 40 minutes of teaching time a week away from subject lessons",
        "evidence_stat": "the teachers who rate pupils' attention usually know which pupils are taking part",
    },
    {  # adaptive-reuse building projects
        "place": "the Polish city of Łódź",
        "start_year": "2016",
        "founder": "a local developer",
        "origin_event": "proposed converting a disused textile mill into workspace after demolition had already been approved",
        "early_scale": "brought 1,200 square metres back into use",
        "current_scale": "9,000 square metres let to 40 businesses",
        "recent_year": "2024",
        "annual_budget": "1.4 million złoty",
        "benefit_stat": "a carbon audit found that the conversion used 62% less embodied carbon than demolition and an equivalent new building would have",
        "cost_stat": "low ceilings and closely spaced columns rule out about 15% of the floor area for modern office use",
        "evidence_stat": "the audit measured construction only, and the converted building uses 30% more heating energy per square metre than a new one would",
    },
    {  # community information networks
        "place": "the borough of Wigan in north-west England",
        "start_year": "2017",
        "founder": "a group of residents",
        "origin_event": "started a neighbourhood newsletter after the last local paper closed and council meetings went unreported",
        "early_scale": "produced a monthly newsletter for one ward",
        "current_scale": "a website read by about 18,000 people a month, filed by 30 volunteer reporters",
        "recent_year": "2024",
        "annual_budget": "£85,000",
        "benefit_stat": "some 74% of readers surveyed said they felt better informed about council decisions than before the site existed",
        "cost_stat": "three of the borough's 25 wards accounted for more than half of all stories published in 2024",
        "evidence_stat": "the ten most-read articles of 2024 were all about crime or planning disputes",
    },
    {  # urban wildlife corridors
        "place": "the Belgian city of Ghent",
        "start_year": "2016",
        "founder": "a wildlife trust officer",
        "origin_event": "persuaded eight neighbouring households to leave connected strips of their gardens unmown",
        "early_scale": "linked eight gardens along one block",
        "current_scale": "a four-kilometre corridor running through 130 gardens and public verges",
        "recent_year": "2024",
        "annual_budget": "€45,000",
        "benefit_stat": "camera traps recorded three times as many hedgehog crossings in 2024 as in 2018, and pollinator counts doubled",
        "cost_stat": "eleven households have left the scheme since 2020, leaving two gaps that break the corridor in half",
        "evidence_stat": "most sightings are logged by residents who have become more attentive since joining, which may exaggerate the increase",
    },
]

ACTORS_SHORT = "those involved"


def derive(base, ctx):
    d = dict(base)
    d.update(ctx)
    d["Subject_cap"] = cap(base["subject"])
    d["Tension_cap"] = cap(base["tension"])
    d["Hidden_cost_cap"] = cap(base["hidden_cost"])
    d["Evidence_tool_cap"] = cap(base["evidence_tool"])
    d["Governance_body_cap"] = cap(base["governance_body"])
    d["Benefit_primary_cap"] = cap(base["benefit_primary"])
    d["Benefit_stat_cap"] = cap(ctx["benefit_stat"])
    d["Cost_stat_cap"] = cap(ctx["cost_stat"])
    d["Evidence_stat_cap"] = cap(ctx["evidence_stat"])
    d["actors_short"] = ACTORS_SHORT
    return d


def angle_origins(f):
    return [
        (
            "{Subject_cap} in {place} began in {start_year}, when {founder} {origin_event}. "
            "At first the project was small: it {early_scale}. It attracted {actors}, most of whom "
            "joined without any formal recruitment. The project grew faster than anyone had expected, and by "
            "{recent_year} the initiative had reached {current_scale}. Looking back, it is clear that "
            "nothing about this was planned in advance. The project developed step by step, as local "
            "people identified needs that existing services were not meeting."
        ).format(**f),
        (
            "The initiative now runs on {daily_mechanism}. Funding comes from {funding_model}, and the "
            "running costs come to about {annual_budget} a year. Because most of that money is "
            "confirmed only twelve months at a time, planning beyond the current year is difficult. "
            "{actors_short_cap} therefore rely on routines that can be adjusted quickly when funding or "
            "staffing changes. To an outside visitor the arrangement can look casual, but in practice it "
            "demands a good deal of coordination."
        ).format(actors_short_cap=cap(f["actors_short"]), **f),
        (
            "Evidence about how well the initiative works comes from {evidence_tool}. These records show "
            "that {benefit_primary}. {Benefit_stat_cap}. Staff and volunteers also rely on experience "
            "that is rarely written down, and they often notice a change on the ground months before the "
            "figures confirm it. The evidence is useful rather than conclusive, however, because "
            "{evidence_dispute}."
        ).format(**f),
        (
            "The main difficulty is not a single crisis but a series of smaller pressures. {Cost_stat_cap}. "
            "There is also a less visible problem: {hidden_cost}. A larger organisation could absorb "
            "setbacks of this kind, but on a budget of {annual_budget} there is very little margin for "
            "error. Underlying all of this is a tension that better management cannot remove: {tension}."
        ).format(**f),
        (
            "The next decision facing the initiative is {future_choice}. Neither option is "
            "straightforward, and there is a further risk to consider: {scaleup_risk}. Most of {actors_short} "
            "would rather change the model gradually than redesign it completely. Their argument is that "
            "much of what makes the initiative work is local knowledge built up since {start_year}, and "
            "that such knowledge would be easy to lose and slow to rebuild."
        ).format(**f),
    ]


def angle_benefits(f):
    return [
        (
            "{Subject_cap} were set up in {place} in {start_year} with one clear aim, and on that measure "
            "the initiative has succeeded. {Benefit_primary_cap}. {Benefit_stat_cap}. This record "
            "explains why {actors} have continued to give their time, and it is the argument used "
            "whenever funding comes up for review. What nobody predicted is how many of the initiative's "
            "effects would fall outside the original aim altogether."
        ).format(**f),
        (
            "The daily routine — {daily_mechanism} — was designed to deliver that aim as efficiently as "
            "possible. In practice the results have been mixed. {Tension_cap}. Concentrating on the "
            "stated benefit can therefore weaken the very conditions that allowed the initiative to "
            "succeed in the first place, and several of the costs took years to become visible."
        ).format(**f),
        (
            "{Evidence_tool_cap} all support the central claim, and the experience of {actors_short} points "
            "in the same direction. The same sources, though, reveal a weakness in the evidence: "
            "{evidence_dispute}. {Evidence_stat_cap}. The recorded benefits are therefore likely to be "
            "somewhat overstated. This matters less when the figures are used to justify continuing than "
            "when they are used to justify expansion."
        ).format(**f),
        (
            "The costs that were not advertised at the start are now the hardest to manage. "
            "{Cost_stat_cap}, and the underlying reason is that {hidden_cost}. With about {annual_budget} "
            "a year to work with, dealing with one problem usually means neglecting another. Discussing "
            "these costs openly would be more honest, but {actors_short} are aware that it might also "
            "weaken the public support the initiative depends on."
        ).format(**f),
        (
            "Any realistic plan must now weigh {future_choice}. There is a further risk either way: "
            "{scaleup_risk}. The easier approach is to keep repeating the original promise and manage "
            "the less visible costs "
            "quietly. A more open approach would set out both sides of the account, even though a "
            "complicated message is harder to defend than the simple one that has worked so far."
        ).format(**f),
    ]


def angle_measurement(f):
    return [
        (
            "Measuring the success of {subject} in {place} is harder than it looks, because the "
            "initiative was never designed with evaluation in mind. In {start_year}, when {founder} "
            "{origin_event}, record-keeping was not a priority, and systematic data collection began "
            "several years later. The early period is therefore documented mainly through the "
            "recollections of {actors}. These are valuable, but they cannot be checked in the way that a "
            "formal dataset can."
        ).format(**f),
        (
            "Current practice relies on {evidence_tool}. These records are produced as a by-product of "
            "{daily_mechanism}, rather than by a purpose-built monitoring system. The advantage is that "
            "they cost almost nothing to collect and interrupt nobody's work. The disadvantage is that "
            "{evidence_dispute}. {Evidence_stat_cap}. Anyone who treats these figures as precise is "
            "asking more of them than they can deliver."
        ).format(**f),
        (
            "The strongest evidence concerns the initiative's central claim. {Benefit_stat_cap}, and both "
            "the records and the impressions of {actors_short} agree that {benefit_primary}. The evidence "
            "on costs is much weaker. {Hidden_cost_cap}, yet that effect is rarely captured by the "
            "existing measures, so it seldom appears in any summary of performance. The difference lies "
            "in how well each side is measured, not necessarily in how much each side matters."
        ).format(**f),
        (
            "{Governance_body_cap} has to decide how much weight to give figures that are known to be "
            "imperfect. {Cost_stat_cap}. The reasons behind that figure, though, are disputed. "
            "Treating the numbers as reliable can lead to decisions that later prove mistaken. Dismissing "
            "them as worthless hands the argument to whoever speaks most persuasively. Both errors have "
            "been made at different points since {start_year}."
        ).format(**f),
        (
            "Improving the evidence would mean paying for measurement that the initiative has so far "
            "managed without, and there is a familiar objection: {scaleup_risk}. A smaller step would be "
            "to review the existing records for the specific weakness described above, namely that "
            "{evidence_dispute}. A review of that kind could be completed within a single funding year "
            "and would at least show how far the current figures can be trusted."
        ).format(**f),
    ]


def angle_future(f):
    return [
        (
            "Decisions about {subject} in {place} were made informally from the beginning. In "
            "{start_year}, {founder} {origin_event}, and nobody set out who would have the authority to "
            "change direction later. That arrangement suited a project that {early_scale}. It fits far "
            "less comfortably now that the initiative has reached {current_scale}, because decisions "
            "today affect many more people than {actors}."
        ).format(**f),
        (
            "{Governance_body_cap} now oversees the initiative. Its relationship with the day-to-day "
            "judgement of {actors_short}, who manage {daily_mechanism}, has never been written down "
            "clearly. Authority is shared in practice but not divided on paper. {Tension_cap}. The "
            "arrangement works well enough while everyone agrees on priorities, but it becomes difficult "
            "as soon as a genuine disagreement arises."
        ).format(**f),
        (
            "When contested decisions have to be made, the evidence offered is largely {evidence_tool}. "
            "Some people find it convincing and others do not, partly because {evidence_dispute}. "
            "{Cost_stat_cap}, and the same evidence has been used to support opposite conclusions. "
            "Governance can therefore feel less like weighing evidence and more like a negotiation "
            "between people who already know what they want the evidence to show."
        ).format(**f),
        (
            "The central dilemma is {future_choice}. It is made harder by the fact that {scaleup_risk}. "
            "Whichever way the decision goes, part of the initiative's original character will be lost, "
            "and {actors_short} are unlikely to agree in advance about which losses are acceptable. "
            "Postponing the decision is not a neutral option either, because the initiative carries a "
            "known cost in the meantime: {hidden_cost}."
        ).format(**f),
        (
            "What happens next will depend less on new evidence than on which priority is chosen when the "
            "trade-offs return. A defensible process would state that choice openly, explaining why "
            "{future_choice} has been settled one way rather than the other. The alternative, which has "
            "been the pattern since {start_year}, is that the outcome is decided by default through "
            "annual funding decisions that nobody describes as a governance choice at all."
        ).format(**f),
    ]


ANGLE_FUNCS = {
    "origins_and_daily_operation": angle_origins,
    "benefits_and_unexpected_costs": angle_benefits,
    "measurement_and_evidence": angle_measurement,
    "future_choices_and_governance": angle_future,
}


def main():
    data_dir = os.path.join("data", "B2")
    files = sorted(glob.glob(os.path.join(data_dir, "*.json")))
    grid = [p for p in files if os.path.basename(p) < "B2_321"]
    assert len(grid) == 80, "expected 80 grid B2 files, found {}".format(len(grid))
    assert len(CONTEXT) == len(BASE_DOMAINS) == 20

    updated = 0
    for group_index, group_start in enumerate(range(0, 80, 4)):
        fields = derive(BASE_DOMAINS[group_index], CONTEXT[group_index])
        for filepath in grid[group_start:group_start + 4]:
            angle = None
            for a in ANGLE_ORDER:
                if "_{}_in_".format(a) in os.path.basename(filepath):
                    angle = a
                    break
            if angle is None:
                raise ValueError("Could not determine angle for {}".format(filepath))

            with open(filepath, encoding="utf-8") as fh:
                doc = json.load(fh)

            paragraphs = ANGLE_FUNCS[angle](fields)

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

    print("Updated {} B2 passages.".format(updated))


if __name__ == "__main__":
    main()
