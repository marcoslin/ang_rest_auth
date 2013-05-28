angular.module("jsonServices", ['ngResource', 'ngCookies', 'ng'])
    .factory('ContactNames', function ($resource) {
        return $resource("/json/name/:id");
    })
    .factory('HTTPHeaders', function ($resource) {
        return $resource("/json/headers");
    });
