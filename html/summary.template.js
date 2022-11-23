/**
 * summary.template.js
 * Template for a summary statement at the begining of the "gas" page
 * Modify at discretion and store as summary.js. If it contains a function called calcCost, its result will be shown on the gas page.
 * Example:
*/

// Diese are values you can get from your last anual gas bill:
var StartVal = 848;					// gas meter counter at the begining of the year
var PricePer_kWh = 0.04675;
var zVal = 0.9374;					// some correction value
var HeatVal = 11.29;				// kWh equivalent for one m³ of gas
var anticipated_per_month = 128;	// monthly advance payment
var mwst = 1.19;					// tax factor
var anual_base = 174.84-37.82;		// base price per year								

function calcCost(tab) {
	let d = new Date();
	let months = d.getMonth();
	let anti = months * anticipated_per_month;
	let base = months *  anual_base / 12;
	let tbl = tab.rows;
	let cur = tbl[tbl.length-1][1];
	let price = base + (cur - StartVal) * HeatVal * PricePer_kWh * zVal * mwst;
	return 	`Payment due for this year <b>${price.toFixed(2)} Kröten</b> (incl. tax and part of base price).<br>` + 
			`Until now <b>${anti} Kröten</b> advance was payed.`;
}
		
