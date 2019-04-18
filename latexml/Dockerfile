FROM mathwebsearch/latexml-mws  

COPY nlab.opt /opt/ltxmojo/
COPY nlab.sty /opt/ltxmojo/
COPY nlab.ltxml /opt/ltxmojo/
RUN chmod +w /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ a\preload = nlab.ltxml' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ a\preload = mathtools.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = mathrsfs.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = graphicx.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = mathtools.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = hyperref.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = color.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = [utf8x]inputenc.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = txfonts.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = stmaryrd.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = revsymb.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
RUN sed -i '$ preload = nlab.sty' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
# RUN sed -i '$ a\profile = nlab' /usr/local/share/perl5/site_perl/LaTeXML/resources/Profiles/mwsq.opt
