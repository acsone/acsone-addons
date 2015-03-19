<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
	xmlns:date="http://exslt.org/dates-and-times"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" encoding="utf-8" />
	<xsl:variable name="HEIGHT" select="'100'" />
	<xsl:template match="/">
		<html>
			<meta http-equiv="content-type"
				content="text/html; charset=utf-8" />

			<body style="background-color:#FF6600;">
				<xsl:for-each select="root/element">
					<div
						style=" width:90%; padding:5px;
						margin-bottom:10px; border:5px double black;
						color:black; background-color:white;
						border-radius:20px;
						text-align:left">
						<xsl:apply-templates select="type" />
						<table
							style='font-family: "Calibri","Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
						    font-size: 12px;
						    margin: 10px 0;
						    width: 100%;
						    text-align: left;
						    border-collapse: collapse;'>
                            
							<xsl:apply-templates select="list" />
						</table>
					</div>
				</xsl:for-each>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="type">
		<h2 style='font-family: "Calibri","Lucida Sans Unicode", "Lucida Grande", Sans-Serif;text-align:center;"'>
			<xsl:value-of select="." disable-output-escaping="yes" />
		</h2>
	</xsl:template>
	<xsl:template match="list">
		<tbody
			style="repeat-x;
    	color: #339;
		">
			<tr
				style="  background: #e8edff;
			    font-size: 16px;
			    color: #99c;
			    text-align:center;">
				<td bgcolor="#00838E" height="{$HEIGHT}"
					style="padding: 8px;
			    border-bottom: 1px solid #fff;
			    color: #FF6600;
			    border-top: 1px solid #fff;
			    background: repeat-x;"
					width="20%">
					<h3>
						<xsl:value-of select="@name" />
					</h3>

					<xsl:apply-templates select="field" />

				</td>
			</tr>
		</tbody>
	</xsl:template>
	<xsl:template match="field">
		<ul>
			<li style="color:#5a471d">
				<xsl:value-of select="." disable-output-escaping="yes" />
			</li>
		</ul>
	</xsl:template>

</xsl:stylesheet>