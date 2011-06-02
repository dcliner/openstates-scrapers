import re

from billy.scrape import NoDataForPeriod
from billy.scrape.committees import CommitteeScraper, Committee

import lxml.html


class OKCommitteeScraper(CommitteeScraper):
    state = "ok"

    def scrape(self, chamber, term):
        if term != '2011-2012':
            raise NoDataForPeriod(term)

        if chamber == "upper":
            self.scrape_upper()
        elif chamber == "lower":
            self.scrape_lower()

    def scrape_lower(self):
        url = "http://www.okhouse.gov/Committees/Default.aspx"
        page = lxml.html.fromstring(self.urlopen(url))
        page.make_links_absolute(url)

        for link in page.xpath("//a[contains(@href, 'Members')]"):
            name = link.xpath("string()").strip()

            if 'Members' in name or 'Conference' in name or 'Joint' in name:
                continue

            self.scrape_lower_committee(name, link.attrib['href'])

    def scrape_lower_committee(self, name, url):
        page = lxml.html.fromstring(self.urlopen(url))
        page.make_links_absolute(url)

        comm = Committee('lower', name)
        comm.add_source(url)

        for link in page.xpath("//a[contains(@href, 'District')]"):
            member = link.xpath('string()').strip()
            member = re.sub(r'\s+', ' ', member)

            if not member:
                continue

            match = re.match(r'((Vice )?Chair)?Rep\. ([^\(]+)', member)
            member = match.group(3).strip()
            role = match.group(1) or 'member'

            comm.add_member(member, role.lower())

        self.save_committee(comm)

    def scrape_upper(self):
        url = "http://www.oksenate.gov/Committees/standingcommittees.htm"
        page = lxml.html.fromstring(self.urlopen(url))
        page.make_links_absolute(url)

        for link in page.xpath("//a[contains(@href, 'standing/')]"):
            name = link.text.strip()
            name = re.sub(r'\s+', ' ', name)
            if 'Committee List' in name:
                continue

            self.scrape_upper_committee(name, link.attrib['href'])

    def scrape_upper_committee(self, name, url):
        page = lxml.html.fromstring(self.urlopen(url))

        comm = Committee('upper', name)
        comm.add_source(url)

        for link in page.xpath("//a[contains(@href, 'biographies')]"):
            member = link.xpath("string()").strip()
            member = re.sub(r'\s+', ' ', member)
            if not member:
                continue
            comm.add_member(member)

        self.save_committee(comm)
