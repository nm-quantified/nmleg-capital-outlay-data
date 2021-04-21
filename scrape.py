import csv
from dataclasses import dataclass
import re

from PyPDF2 import PdfFileReader


@dataclass
class Sponsor:
    name: str
    amount: int


@dataclass
class ProjectSponsor:
    project_name: str
    locale: str
    agency: str
    web_id: int
    sponsor_name: str
    sponsor_amount: int


def clean(content: str) -> str:
    footer = r"Monday\,\sApril\s19\,\s2021\nPage\s\d+\sof\s166\n4\:22\sPM\nChart\sFunded\sProjects\sby\sCounty\sw\/\sSponsor"
    header = r"Capital\sOutlay\sProjects\nChart\sby\sSponsor\s\nChap\/Section\nProject\sTitle\nAmount\nCity\/Locale\nAgency\nFund\nLegislative\sCouncil\sService\n55th\sLegislature\s-\sFirst\sSession\s2021\nSponsor\nWebID"
    no_footer = re.sub(footer, "", content)
    no_header = re.sub(header, "", no_footer)
    return no_header


def clean_dollars(amount: str) -> int:
    amount = amount.replace(",", "")
    return int(amount)


def parse(item: str) -> dict:
    data = {}
    project_name_match = re.search(
        r"\d\n(.+)\n(GF|STB|GPF|ERF|FPF|BEGPF|HMF|VSF|PSCOF)\n",
        item,
        re.MULTILINE | re.DOTALL,
    )
    if project_name_match:
        data["project_name"] = project_name_match[1]
    agency_match = re.search(r"\n\s\n.*\n([A-Z\/\d]+)\n\d+", item)
    locale_match = re.search(
        r"(GF|STB|GPF|ERF|FPF|BEGPF|HMF|VSF|PSCOF)\n(VETO|LV|\s)\n\s\n(.+)\n[A-Z]+",
        item,
    )
    if locale_match:
        data["locale"] = locale_match[3]
    if agency_match:
        data["agency"] = agency_match[1]
    else:
        data["agency"] = ""
    sponsors_match = re.findall(r"\n\$(\d+\,*\d*\,*\d*)\n(.+)", item)
    web_id_match = re.search(r"\n[A-Z\/\d]+\n(\d+)\n+\$", item)
    if web_id_match:
        web_id = web_id_match[1]
        data["web_id"] = web_id
    else:
        data["web_id"] = ""
    if sponsors_match:
        sponsors = [
            Sponsor(name=sponsor[1], amount=clean_dollars(sponsor[0])).__dict__
            for sponsor in sponsors_match
        ]
        data["sponsors"] = sponsors
    return data


def generate_project_sponsors(row):
    out = []
    for sponsor in row["sponsors"]:
        project_sponsor = ProjectSponsor(
            project_name=row.get("project_name", "").replace("\n", ""),
            locale=row.get("locale", ""),
            agency=row["agency"].replace("\n", ""),
            web_id=row["web_id"],
            sponsor_name=sponsor["name"].replace("\n", ""),
            sponsor_amount=sponsor["amount"],
        )
        out.append(project_sponsor.__dict__)
    return out

def main():
    with open("HB_285_Capital_Projects_2021.pdf", "rb") as f:
        reader = PdfFileReader(f)
        page_count = reader.getNumPages()
        pages = [reader.getPage(i).extractText() for i in range(page_count)]
        content = ""
        for page in pages:
            content += page
        cleaned = clean(content)
        items = re.split(r"Project\stotal\safter\svetoes\:\n", cleaned)
        items.pop()
        projects = [parse(item) for item in items]
        project_sponsors = []
        for project in projects:
            project_sponsors += generate_project_sponsors(project)
    with open("HB_285_Capital_Projects_2021.csv", "w") as f:
        writer = csv.DictWriter(
            f,
            [
                "sponsor_name",
                "locale",
                "agency",
                "project_name",
                "web_id",
                "sponsor_amount",
            ],
        )
        writer.writeheader()
        writer.writerows(project_sponsors)

if __name__ == "__main__":
    main()