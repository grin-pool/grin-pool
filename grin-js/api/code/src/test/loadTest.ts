'use strict';

/**
 * Sample request generator usage.
 * Contributed by jjohnsonvng:
 * https://github.com/alexfernandez/loadtest/issues/86#issuecomment-211579639
 */
/*
const loadtest = require('loadtest');

const options = {
	url: 'http://localhost:3009/',
	concurrency: 30,
	method: 'GET',
	body:'',
	requestsPerSecond: 200,
	maxSeconds:30,
	requestGenerator: (params, options, client, callback) => {
        const blockHeight = Math.floor(Math.random() * 2000)
        const blockRange = Math.floor(Math.random() * 110)
        const url = `http://localhost:3009/pool/stats/${blockHeight},${blockRange}/gps,height,total_blocks_found,active_miners,timestamp,edge_bits`
        console.log('url is: ', url)
		options.path = url
		const request = client(options, callback)
		return request;
	}
};

loadtest.loadTest(options, (error, results) => {
	if (error) {
		return console.error('Got an error: %s', error);
	}
	console.log(results);
	console.log('Tests run successfully');
});
*/