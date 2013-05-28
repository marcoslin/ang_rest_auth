'use strict';

angular.module('AngRestAuthApp', ['jsonServices','angular-rest-auth'])
    .config(function ($routeProvider) {
        // Note: only route defined with require_auth:true will be checked for Authorization
        $routeProvider
            .when('/', { templateUrl: 'views/home.html', controller: 'MainCtrl' } )
            .when('/headers', { templateUrl: 'views/headers.html', controller: 'HeadersCtrl' } )
            .when('/login', { templateUrl: 'views/login.html', controller: 'LoginCtrl' } )
            .when('/main', { templateUrl: 'views/main.html', controller: 'MainCtrl', require_auth: true } )
            .when('/list', { templateUrl: 'views/list.html', controller: 'ListCtrl', require_auth: true } )
            .when('/detail/:id', { templateUrl: 'views/detail.html', controller: 'DetailCtrl', require_auth: true } )
            .otherwise({ redirectTo: '/' });
    }).run(function (Authenticate) {
        Authenticate.initialize();
    });

