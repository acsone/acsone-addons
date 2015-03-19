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
                <xsl:for-each select="version/we:Skills">
                    <xsl:variable name="WIDTH">
                        <xsl:value-of select="@arg" />
                    </xsl:variable>
                    <div
                        style="float:left; width:{$WIDTH}%; padding:5px;
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
                                <tr
                                    style="  background: #e8edff;
                                        font-size: 16px;
                                        color: #99c;
                                        text-align:center;">
                                    <td bgcolor="#00838E" height="75px"
                                        style="padding: 8px;
                                        border-bottom: 1px solid black;                                        color:#5a471d;
                                        border-top: 1px solid black;
                                        background: repeat-x;"
                                        width="20%">
                                        <xsl:if
                                            test="@locale !='nl' and @locale != 'fr'">
                                            <h3
                                                style="text-align:center;color: #FF6600;">
                                                Skills
                                            </h3>
                                            <br />
                                        </xsl:if>
                                        <xsl:if test="@locale='fr'">
                                            <h3
                                                style="text-align:center;color: #FF6600;">
                                                Compétences
                                            </h3>
                                            <br />
                                        </xsl:if>
                                        <xsl:if test="@locale='nl'">
                                            <h3
                                                style="text-align:center;color: #FF6600;">
                                                Vaardigheden
                                            </h3>
                                            <br />
                                        </xsl:if>
                                    </td>
                                </tr>
                                <xsl:apply-templates
                                    select="we:Linguistic">
                                    <xsl:with-param name="language"
                                        select="@locale" />
                                </xsl:apply-templates>

                                <xsl:apply-templates
                                    select="we:Computer" />
                            </tbody>
                        </table>
                    </div>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="we:Computer">
        <tr
            style="  background: #e8edff;
			    font-size: 16px;
			    color: #99c;
			    text-align:center;">
            <td bgcolor="#00838E" height="{$HEIGHT}"
                style="padding: 8px;
			    border-bottom: 1px solid black;
			    color:#5a471d;
			    border-top: 1px solid #fff;
			    background: repeat-x;"
                width="20%">
                <xsl:apply-templates select="we:Description" />
            </td>
        </tr>
    </xsl:template>
    <xsl:template match="we:Linguistic">
        <xsl:param name="language"></xsl:param>
        <tr
            style="  background: #e8edff;
			    font-size: 16px;
			    color: #99c;
			    text-align:center;">
            <td bgcolor="#00838E" height="{$HEIGHT}"
                style="padding: 8px;
			    border-bottom: 1px solid black;
			    color:#5a471d;
			    border-top: 1px solid #fff;
			    background: repeat-x;
                "
                width="20%">
                <xsl:apply-templates select="we:MotherTongueList">
                </xsl:apply-templates>
                <xsl:apply-templates select="we:ForeignLanguageList">
                    <xsl:with-param name="language" select="$language" />
                </xsl:apply-templates>
            </td>
        </tr>
    </xsl:template>

    <xsl:template match="we:MotherTongueList">
        <xsl:apply-templates select="we:MotherTongue" />
    </xsl:template>

    <xsl:template match="we:ForeignLanguageList">
        <xsl:param name="language"></xsl:param>

        <xsl:apply-templates select="we:ForeignLanguage">
            <xsl:with-param name="language" select="$language" />
        </xsl:apply-templates>
    </xsl:template>

    <xsl:template match="we:MotherTongue">
        <xsl:apply-templates select="we:Description/we:Label" />
    </xsl:template>

    <xsl:template match="we:ForeignLanguage">
        <xsl:param name="language"></xsl:param>
        <xsl:apply-templates select="we:Description/we:Label" />
        <ul>
            <xsl:apply-templates select="we:ProficiencyLevel">
                <xsl:with-param name="language" select="$language" />
            </xsl:apply-templates>
        </ul>
    </xsl:template>


    <xsl:template match="we:ProficiencyLevel">
        <xsl:param name="language"></xsl:param>
        <xsl:apply-templates select="we:Listening">
            <xsl:with-param name="language" select="$language" />
        </xsl:apply-templates>
        <xsl:apply-templates select="we:Reading">
            <xsl:with-param name="language" select="$language" />
        </xsl:apply-templates>
        <xsl:apply-templates select="we:SpokenInteraction">
            <xsl:with-param name="language" select="$language" />
        </xsl:apply-templates>
        <xsl:apply-templates select="we:SpokenProduction">
            <xsl:with-param name="language" select="$language" />
        </xsl:apply-templates>
        <xsl:apply-templates select="we:Writing">
            <xsl:with-param name="language" select="$language" />
        </xsl:apply-templates>
    </xsl:template>

    <xsl:template match="we:Listening">
        <xsl:param name="language"></xsl:param>
        <!--TRANSLATE
            TO translate:
            copy paste a new line of this:
            <xsl:if test="$language ='en'">- "TEXT" :</xsl:if>
            
            Change the 'en' with the abstract language you find in Europass
            (fr, es...)
            replace the text into " " by the traduction.
        -->

        <xsl:if test="$language ='en'">- "Listening" :</xsl:if>
        <xsl:if test="$language ='fr'">"Écouter" :</xsl:if>
        <xsl:if test="$language ='ne'">"Luisteren" :</xsl:if>

        <xsl:value-of select="." />
        <br />
    </xsl:template>

    <xsl:template match="we:Reading">
        <xsl:param name="language"></xsl:param>
        <!--TRANSLATE
            TO translate:
            copy paste a new line of this:
            <xsl:if test="$language ='en'">- "TEXT" :</xsl:if>
            
            Change the 'en' with the abstract language you find in Europass
            (fr, es...)
            replace the text into " " by the traduction.
        -->
        <xsl:if test="$language ='en'">- "Reading" :</xsl:if>
        <xsl:if test="$language ='fr'">"Lire" :</xsl:if>
        <xsl:if test="$language ='ne'">"Lezen" :</xsl:if>

        <xsl:value-of select="." />
        <br />
    </xsl:template>

    <xsl:template match="we:SpokenInteraction">
        <xsl:param name="language"></xsl:param>
        <!--TRANSLATE
            TO translate:
            copy paste a new line of this:
            <xsl:if test="$language ='en'">- "Spoken interaction" :</xsl:if>
            
            Change the 'en' with the abstract language you find in Europass
            (fr, es...)
            replace the text into " " by the traduction.
        -->

        <xsl:if test="$language ='en'">- "Spoken interaction" :</xsl:if>
        <xsl:if test="$language ='fr'">
            "Dialoguer" :
        </xsl:if>
        <xsl:if test="$language ='ne'">"Interactie" :</xsl:if>

        <xsl:value-of select="." />
        <br />
    </xsl:template>

    <xsl:template match="we:SpokenProduction">
        <xsl:param name="language"></xsl:param>
        <!--TRANSLATE
            TO translate:
            copy paste a new line of this:
            <xsl:if test="$language ='en'">- "TEXT" :</xsl:if>
            
            Change the 'en' with the abstract language you find in Europass
            (fr, es...)
            replace the text into " " by the traduction.
        -->

        <xsl:if test="$language ='en'">- "Spoken production" :</xsl:if>
        <xsl:if test="$language ='fr'">
            "Parler en continu" :
        </xsl:if>
        <xsl:if test="$language ='ne'">"Productie" :</xsl:if>

        <xsl:value-of select="." />
        <br />
    </xsl:template>

    <xsl:template match="we:Writing">
        <xsl:param name="language"></xsl:param>
        <!--TRANSLATE
            TO translate:
            copy paste a new line of this:
            <xsl:if test="$language ='en'">- "TEXT" :</xsl:if>
            
            Change the 'en' with the abstract language you find in Europass
            (fr, es...)
            replace the text into " " by the traduction.
        -->

        <xsl:if test="$language ='en'">- "Writing":</xsl:if>
        <xsl:if test="$language ='fr'">"Écrire" :</xsl:if>
        <xsl:if test="$language ='ne'">"Schrijven" :</xsl:if>

        <xsl:value-of select="." />
        <br />
    </xsl:template>

    <xsl:template match="we:Description/we:Label">
        <ul>
            <li>
                <xsl:value-of select="." disable-output-escaping="yes" />
            </li>
        </ul>
    </xsl:template>
    <xsl:template match="we:Description">
        <xsl:value-of select="." disable-output-escaping="yes" />
    </xsl:template>
</xsl:stylesheet>
