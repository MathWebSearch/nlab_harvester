FROM mathwebsearch/latexml-mws  

COPY nlab.opt /opt/ltxmojo/
COPY nlab.sty /opt/ltxmojo/
COPY nlab.ltxml /opt/ltxmojo/
RUN chmod +w /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ a\preload = nlab.ltxml' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
