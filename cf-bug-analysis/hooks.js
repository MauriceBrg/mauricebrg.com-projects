module.exports = {
  logAndMetrics: function(requestParams, response, context, event, next) {
    if (response.statusCode === 500) {
    //   console.log(`Path: ${requestParams.url}`);
    //   console.log(`Non-200 response: ${response.statusCode}`);
      // console.log('Headers:', response.headers);
      // console.log('Body:', response.body);
    }

    const environment = response.headers.environment || "unknown"
    // Increment counters for the environment and the environment + status code
    event.emit('counter', `environment_${environment}_${response.statusCode}`, 1)
    event.emit('counter', `environment_${environment}`, 1)
    return next();
  }
};