'use strict';

angular.module("unitTestApp", ['angular-rest-auth'])
    .config(function ($routeProvider) {
        // Mock routes
        $routeProvider
            .when('/', { templateUrl: 'views/home.html' } )
            .when('/login', { templateUrl: 'views/login.html' } )
            .when('/main', { templateUrl: 'views/main.html', require_auth: true } )
            .when('/public', { templateUrl: 'views/main.html' } )
            .otherwise({ redirectTo: '/' });
    })
    .run(['$templateCache', 'Authenticate', function ($templateCache, Authenticate) {
        // Mock templates
        $templateCache.put("views/home.html", "<!DOCTYPE html><title>Home</title>");
        $templateCache.put("views/login.html", "<!DOCTYPE html><title>Login</title>");
        $templateCache.put("views/main.html", "<!DOCTYPE html><title>Main</title>");
        // Initialize Authenticate
        Authenticate.initialize();
    }]);

describe('angular-rest-auth: Authenticate Service', function () {
    var authenticate, rootScope, location, http, httpBackend;

    // load the test App
    beforeEach(module('unitTestApp'));

    describe('MAIN', function () {
        var user_name = "tester",
            password = "angular",
            success_login = { "user_name": user_name, "auth_token": "THEAUTHTOKEN" };

        beforeEach(inject(function (Authenticate, $rootScope, $location, $http, $httpBackend, $route ) {
            /**
             * Note: it is critical to load $route and Authenticate, or the redirect won't work.
             * No need to assign then to variable, just declared to be injected is enough.
             */
            authenticate = Authenticate;
            rootScope = $rootScope;
            location = $location;
            http = $http;
            httpBackend = $httpBackend;
            httpBackend.resetExpectations();
        }));

        it("going to protected path should redirect to login", function () {
            //scope.goTo("/main");
            location.path("/main");
            expect(location.path()).toBe("/main");
            rootScope.$digest();
            expect(location.path()).toBe("/login");
        });

        it("going to unprotected path should not redirect to login", function () {
            //scope.goTo("/main");
            location.path("/public");
            expect(location.path()).toBe("/public");
            rootScope.$digest();
            expect(location.path()).toBe("/public");
        });

        it("login on required_auth should call expected resources and redirect to caller.", function () {
            // Ask for main page
            location.path("/main");
            expect(location.path()).toBe("/main");

            // Should be redirected to login page
            rootScope.$digest();
            expect(location.path()).toBe("/login");

            // Login in should POST to resource
            httpBackend.expectPOST("/auth/login").respond(success_login);
            authenticate.login(user_name, password, function(error) {
                console.log("Login failed: ", error);
                expect(true).toBe(false);
            });
            httpBackend.flush();

            // Make sure login worked
            expect(authenticate.get_username()).toBe(user_name);

            // Should be redirected back to main page
            rootScope.$digest();
            expect(location.path()).toBe("/main");
        });


        it("Authorize.check_login() should work same as protected resources.", function () {
            // Ask for main page
            location.path("/public");
            expect(location.path()).toBe("/public");
            authenticate.check_login();

            // Should be redirected to login page
            rootScope.$digest();
            expect(location.path()).toBe("/login");

            // Login in should POST to resource
            httpBackend.expectPOST("/auth/login").respond(success_login);
            authenticate.login(user_name, password, function(error) {
                console.log("Login failed: ", error);
                expect(true).toBe(false);
            });
            httpBackend.flush();

            // Make sure login worked
            expect(authenticate.get_username()).toBe(user_name);

            // Should be redirected back to main page
            rootScope.$digest();
            expect(location.path()).toBe("/public");
        });


        it("401 Unauthorized response from server should redirect to login", function () {
            // Perform login
            httpBackend.expectPOST("/auth/login").respond(success_login);
            authenticate.login(user_name, password, function(error) {
                console.log("Login failed: ", error);
                expect(true).toBe(false);
            });
            httpBackend.flush();

            // Ask for main page
            location.path("/main");
            expect(location.path()).toBe("/main");

            // Make a dummy call returning 401
            httpBackend.expectGET("/dummy").respond(401, 'Unauthorized');
            http.get("/dummy");
            httpBackend.flush();

            // Make sure redirect took place
            expect(location.path()).toBe("/login");
        });

        it("logout should call expected resources.", function () {
            httpBackend.expectGET("/auth/logout").respond();
            authenticate.logout();
        });

    });

});
