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
                <xsl:for-each select="version/we:EducationList">
                    <xsl:variable name="WIDTH">
                        <xsl:value-of select="@arg" />
                    </xsl:variable>
                    <div
                        style="float:left; width:{$WIDTH}%; padding:5px;
						margin-bottom:10px; border:5px double black;
						color:black; background-color:white;
						border-radius:20px;
						text-align:left">

                        <table width="100%"
                            style="border-radius:20px;">
                            <tbody
                                style="repeat-x;
                                color: #339;
                                ">

                                <tr
                                    style="  background: #e8edff;
                                        font-size: 16px;
                                        color: #99c;
                                        text-align:center;
                                        height:20px;
                                        overflow: auto;">
                                    <td bgcolor="#00838E" height="75px"
                                        style="padding: 8px;
                                        border-bottom: 1px solid black;
                                        color:#5a471d;
                                        border-top: 1px solid black;
                                        background: repeat-x;"
                                        width="20%">
                                        <xsl:if
                                            test="@locale !='nl' and @locale != 'fr'">
                                            <h3
                                                style="text-align:center;color: #FF6600;">
                                                Education and training
                                            </h3>
                                            <br />
                                        </xsl:if>
                                        <xsl:if test="@locale='fr'">
                                            <h3
                                                style="text-align:center;color: #FF6600;">
                                                Éducation et formation
                                            </h3>
                                            <br />
                                        </xsl:if>
                                        <xsl:if test="@locale='nl'">
                                            <h3
                                                style="text-align:center;color: #FF6600;">
                                                Onderwijs en Opleiding
                                            </h3>
                                            <br />
                                        </xsl:if>
                                    </td>
                                </tr>
                                <xsl:apply-templates
                                    select="we:Education">
                                    <xsl:with-param name="language"
                                        select="@locale" />
                                </xsl:apply-templates>
                            </tbody>
                        </table>
                    </div>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="we:Education">
        <xsl:param name="language"></xsl:param>
        <tr
            style="  background: #e8edff;
			    font-size: 16px;
			    color: #99c;
			    text-align:center;
                height:20px;
                overflow: auto;">
            <td bgcolor="#00838E" height="{$HEIGHT}"
                style="padding: 8px;
			    border-bottom: 1px solid black;
			    color:#5a471d;
			    border-top: 1px solid black;
			    background: repeat-x;overflow:auto"
                width="20%">
                <xsl:apply-templates select="we:Period">

                    <xsl:with-param name="language" select="$language" />

                </xsl:apply-templates>
                <xsl:apply-templates select="we:Title" />
            </td>
        </tr>
    </xsl:template>
    <xsl:template match="we:Title">
        <p style="text-align:center;color:#59A5DE; text-align:left;">
            <xsl:value-of select="." />
        </p>
    </xsl:template>
    <xsl:template match="we:Period">
        <xsl:param name="language"></xsl:param>
        <xsl:apply-templates select="we:From" />

        <!--TRANSLATE
            TO translate:
            copy paste a new line of this:
            <xsl:if test="$language ='en'">- "TEXT" :</xsl:if>
            
            Change the 'en' with the abstract language you find in Europass
            (fr, es...)
            replace the text into " " by the traduction.
        -->
        <xsl:if test="$language ='en'">to</xsl:if>
        <xsl:if test="$language ='fr'">à</xsl:if>
        <xsl:if test="$language ='ne'">tot</xsl:if>
        <xsl:text>  </xsl:text>
        <xsl:apply-templates select="we:To" />
        <xsl:apply-templates select="we:Current">

            <xsl:with-param name="language" select="$language" />

        </xsl:apply-templates>
        <br />
    </xsl:template>

    <xsl:template match="we:From">
        <xsl:value-of select="@year" />
        <xsl:value-of select="substring(@month,2,4)" />
        <xsl:value-of select="substring(@day,3,5)" />
        <xsl:text>  </xsl:text>
    </xsl:template>
    <xsl:template match="we:To">
        <xsl:value-of select="@year" />
        <xsl:value-of select="substring(@month,2,4)" />
        <xsl:value-of select="substring(@day,3,5)" />
        <xsl:text>  </xsl:text>
    </xsl:template>
    <xsl:template match="we:Current">
        <xsl:param name="language"></xsl:param>
        <xsl:if test="current()='true'">

            <!--TRANSLATE
                TO translate:
                copy paste a new line of this:
                <xsl:if test="$language ='en'">- "TEXT" :</xsl:if>
                
                Change the 'en' with the abstract language you find in Europass
                (fr, es...)
                replace the text into " " by the traduction.
            -->

            <xsl:if test="$language ='en'">now</xsl:if>
            <xsl:if test="$language ='fr'">maintenant</xsl:if>
            <xsl:if test="$language ='ne'">nu</xsl:if>

        </xsl:if>
        <xsl:text>  </xsl:text>
    </xsl:template>
</xsl:stylesheet>
