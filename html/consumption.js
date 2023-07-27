/**
 * class Consumption
 * operations on the gas consumption table
 */
 
 class Consumption {
	constructor(date, value) {
		this.date = date;
		this.value = value;
		}
		
	delta(other) {
		return new Consumption(new Date(this.date.valueOf() - other.date.valueOf()), this.value - other.value);
	}
	
	// use only on deltas
	sum(other) {
		return new Consumption(new Date(this.date.valueOf() + other.date.valueOf()), this.value + other.value);
	}
	
	less(other) {
		return this.date.valueOf() < other.date.valueOf();
	}
}