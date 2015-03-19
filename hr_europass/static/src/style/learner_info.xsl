<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:date="http://exslt.org/dates-and-times"
    xmlns:we="http://europass.cedefop.europa.eu/Europass"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="utf-8" />
    <xsl:variable name="HEIGHT" select="'100'" />
    <xsl:template match="/">
        <html>
            <meta http-equiv="content-type"
                content="text/html; charset=utf-8" />
            <body>
                <xsl:for-each select="version/we:LearnerInfo">
                    <xsl:variable name="WIDTH">
                        <xsl:value-of select="@arg" />
                    </xsl:variable>
                    <div
                        style="float:left;width:{$WIDTH}%; padding:5px;
						margin-bottom:10px; border:5px double black;
						color:black; background-color:white;
						border-radius:20px;
						text-align:left">
                        <table wight="100%"
                            style="border-radius:20px;">
                            <tbody
                                style="repeat-x;
                                color: #339;
                                ">
                                <xsl:if
                                    test="@locale != 'fr' and @locale != 'nl' and @locale != 'en'">
                                    <h1
                                        style="5px solid;text-align:center;color: #FF6600;">
                                        <xsl:value-of select="@locale" />
                                    </h1>
                                    <br />
                                </xsl:if>
                                <xsl:if test="@locale='en'">
                                    <h1
                                        style="5px solid;text-align:center;color: #FF6600;">
                                        English
                                    </h1>
                                    <br />
                                </xsl:if>
                                <xsl:if test="@locale='fr'">
                                    <h1
                                        style="5px solid;text-align:center;color: #FF6600;">
                                        Français
                                    </h1>
                                    <br />
                                </xsl:if>
                                <xsl:if test="@locale='nl'">
                                    <h1
                                        style="5px solid;text-align:center;color: #FF6600;">
                                        Nederlands
                                    </h1>
                                    <br />
                                </xsl:if>
                                <xsl:apply-templates
                                    select="we:Identification" />
                            </tbody>
                        </table>
                    </div>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="we:Identification">
        <xsl:apply-templates select="we:PersonName" />
        <xsl:apply-templates select="we:ContactInfo" />
    </xsl:template>

    <xsl:template match="we:PersonName">

        <strong>
            <xsl:apply-templates select="we:FirstName" />
            <br />
            <xsl:apply-templates select="we:Surname" />
        </strong>
        <br />
    </xsl:template>

    <xsl:template match="we:FirstNamme">
        <xsl:value-of select="." />
    </xsl:template>
    <xsl:template match="we:Surname">
        <xsl:value-of select="." />
    </xsl:template>
    
    <xsl:template match="we:Employer">
        <xsl:apply-templates select="we:Name" />
        <xsl:apply-templates select="we:ContactInfo" />
        <xsl:apply-templates select="we:Sector" />

    </xsl:template>
    <xsl:template match="we:Sector">
        <xsl:apply-templates select="we:Label" />
    </xsl:template>
    <xsl:template match="we:Name">
        <xsl:value-of select="." disable-output-escaping="yes" />
    </xsl:template>
    <xsl:template match="we:ContactInfo">
        <xsl:apply-templates select="we:Address" />
        <xsl:apply-templates select="we:Website" />
        <xsl:apply-templates select="we:Email" />
    </xsl:template>


    <xsl:template match="we:Email">
        <xsl:value-of select="./we:Contact" />
    </xsl:template>

    <xsl:template match="we:Address">
        <xsl:apply-templates select="we:Contact" />
    </xsl:template>
    <xsl:template match="we:Website">
        <xsl:apply-templates select="we:Contact" />
    </xsl:template>
    <xsl:template match="we:Contact">
        <xsl:apply-templates select="we:PostalCode" />
        <xsl:apply-templates select="we:AddressLine" />
        <xsl:apply-templates select="we:Municipality" />
    </xsl:template>
    <xsl:template match="we:PostalCode">
        <xsl:value-of select="." disable-output-escaping="yes" />
        <br />
    </xsl:template>
    <xsl:template match="we:AddressLine">
        <xsl:value-of select="." disable-output-escaping="yes" />
        <br />
    </xsl:template>
    <xsl:template match="we:Municipality">
        <xsl:value-of select="." disable-output-escaping="yes" />
        <br />
    </xsl:template>
    <xsl:template match="we:Country">
        <xsl:apply-templates select="we:Label" />
        <br />
    </xsl:template>
    <xsl:template match="we:Label">
        <xsl:value-of select="." disable-output-escaping="yes" />
    </xsl:template>
</xsl:stylesheet>
