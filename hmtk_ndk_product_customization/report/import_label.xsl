<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
	<xsl:variable name="initial_bottom_pos">24.5</xsl:variable>
	<xsl:variable name="initial_left_pos">0.5</xsl:variable>
	<xsl:variable name="height_increment">4</xsl:variable>
	<xsl:variable name="width_increment">10.7</xsl:variable>
	<xsl:variable name="frame_height">4cm</xsl:variable>
	<xsl:variable name="frame_width">9.3cm</xsl:variable>
	<xsl:variable name="number_columns">2</xsl:variable>
	<xsl:variable name="max_frames">8</xsl:variable>

	<xsl:template match="/">
		<xsl:apply-templates select="lots"/>
	</xsl:template>

	<xsl:template match="lots">
		<document>
			<template leftMargin="2.0cm" rightMargin="2.0cm" topMargin="2.0cm" bottomMargin="2.0cm" title="Address list" author="Generated by Open ERP">
				<pageTemplate id="all">
					<pageGraphics/>
					<xsl:apply-templates select="lot-line" mode="frames"/>
				</pageTemplate>
			</template>
			<stylesheet>
				<paraStyle name="nospace" fontName="Courier" fontSize="4" spaceBefore="0" spaceAfter="0"/>
				<paraStyle name="nospace6bold" fontName="Courier-Bold" fontSize="4" spaceBefore="0" spaceAfter="0" bold="1"/>
				<paraStyle name="nospace6" fontName="Courier" fontSize="4" spaceBefore="4" spaceAfter="0"/>
				<blockTableStyle id="mytable">
					<blockBackground colorName="lightgrey" start="0,0" stop="0,0"/>
					<blockAlignment value="LEFT"/>
					<blockValign value="LEFT"/>
					<blockFont name="Helvetica-BoldOblique" size="14" start="0,0" stop="-1,0"/>
					<lineStyle kind="GRID" colorName="black" tickness="1"/>
				</blockTableStyle>
			</stylesheet>
			<story>
				<xsl:apply-templates select="lot-line" mode="story"/>
			</story>
		</document>
	</xsl:template>

	<xsl:template match="lot-line" mode="frames">
		<xsl:if test="position() &lt; $max_frames + 1">
			<frame>
				<xsl:attribute name="width">
					<xsl:value-of select="$frame_width"/>
				</xsl:attribute>
				<xsl:attribute name="height">
					<xsl:value-of select="$frame_height"/>
				</xsl:attribute>
				<xsl:attribute name="x1">
					<xsl:value-of select="$initial_left_pos + ((position()-1) mod $number_columns) * $width_increment"/>
					<xsl:text>cm</xsl:text>
				</xsl:attribute>
				<xsl:attribute name="y1">
					<xsl:value-of select="$initial_bottom_pos - floor((position()-1) div $number_columns) * $height_increment"/>
					<xsl:text>cm</xsl:text>
				</xsl:attribute>
			</frame>
		</xsl:if>
	</xsl:template>

    <xsl:param name="pmaxChars" as="xs:integer" select="80"/>

	<xsl:template match="lot-line" mode="story">
            <blockTable style="mytable" colWidths="6.00cm" rowHeights="3cm">
                <tr>
                    <td>
                    	<para style="nospace6bold"><xsl:text>Business Importer</xsl:text></para>
                        <para style="nospace"><xsl:value-of select="businessimporter"/></para>
                        <para style="nospace">
	                        <xsl:value-of select="street"/>
	                        <xsl:text>,</xsl:text><xsl:value-of select="street2"/>
	                        <xsl:text>,</xsl:text><xsl:value-of select="mxcity2"/>
	                        <xsl:text>,</xsl:text><xsl:value-of select="city"/>
	                        <xsl:text>,</xsl:text><xsl:value-of select="state"/>
	                        <xsl:text>,</xsl:text><xsl:value-of select="country"/>
	                        <xsl:text>,</xsl:text><xsl:value-of select="zip"/>
                        </para>
                        <para style="nospace"><xsl:text>Made in:</xsl:text><xsl:value-of select="made_in"/>
                        </para>
                        <para style="nospace"><xsl:text>Brand:</xsl:text><xsl:value-of select="brand"/>
                        </para>
                        <para style="nospace"><xsl:text>Model:</xsl:text><xsl:value-of select="model"/>
                        </para>
                        <para style="nospace"><xsl:text>Content:</xsl:text><xsl:value-of select="content"/>
                        </para>
                        <para style="nospace"> <xsl:value-of select="electrical_properties"/>
                        </para>
                    </td>
                </tr>
                
            </blockTable>
	<nextFrame/>
	</xsl:template>
</xsl:stylesheet>