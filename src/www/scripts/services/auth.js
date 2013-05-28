/**
 * Authenticate is wrapped in a service in auth.js.  Following are needed to setup authentication:
 *   1. auth.js must be source by index.html
 *   2. Protected route must be defined with parameter 'require_auth: true'
 *   3. ng-app must call Authenticate.initialize([login_route]) on .run
 *
 *
 * In other words:
 *   .config allow for $httpProvider but not Authenticate
 *   .run allow for Authenticate but not $httpProvider
 *
 * So, only logic under .run can be moved into the Authenticate service.
 *
 * Reference:
 *   URL: http://docs.angularjs.org/guide/module
 *   Section: "Module Loading & Dependencies"
 *
 * ToDo:
 *   * Create initialization parameters allowing changing of login resources
 *   * Implement support for Basic and Digest HTTP Authentication
 *   * Implement/Test support for HTTPS
 *
 */

angular.module('angular-rest-auth', ['ngResource', 'ngCookies'])
    .service('Authenticate', function ($resource, $cookieStore, $rootScope, $http, $location, $window, $log) {
        'use strict';
        var self = this,
            auth_key = "Authorization",
            source_url_key = "source_url",
            login_path = "/login", // Default login path
            logged_in_user;

        /**
         * Private Methods
         * ToDo: Make $resource configurable
         */
        var login_service = $resource("/auth/:action", {}, {
            login: { method: "POST", params: {action: "login"} },
            logout: { method: "GET",  params: {action: "logout"} }
        });

        var set_auth_header = function (header_data) {
            // Set the headers.common so all $resource call will pass the header_data
            // to the server.
            if ( $http.defaults.headers.common ) {
                $http.defaults.headers.common[auth_key] = header_data;
            } else {
                var auth_header = {};
                auth_header[auth_key] = data.auth_token;
                $http.defaults.headers.common = auth_header;
            }
        };

        var clear_login_info = function () {
            $log.info("Authenticate: clearing login info for auth_key: " + auth_key);
            logged_in_user = "";
            delete $http.defaults.headers.common[auth_key];
            $cookieStore.remove(auth_key);
        };

        var check_logged_in = function () {
            // If user is not logged in, raise the login event
            if ( !self.get_username() ) {
                $rootScope.$broadcast('event:login:required');
            }
        };

        var ask_user_to_login = function () {
            var cur_path = $location.path();
            if ( cur_path ) {
                $location.path(login_path).search(source_url_key, cur_path);
            } else {
                $location.path(login_path);
            }
        };

        var get_source_url = function () {
            // ToDo: Remove the hard coded /main
            var location_search = $location.search();
            return location_search[source_url_key] || '/main';
        }

        /**
         * Public Methods
         */
        this.initialize = function (login_route) {
            // Allow overriding of the default login route
            $log.info("Authenticate: initialize called.");
            if (login_route) {
                login_path = login_route;
            }

            //Listen to events published to $rootScope
            $rootScope.login_in_progress = false; // When set to true, stop intercepting 401 http response

            // Emit a login require event on a protected route
            $rootScope.$on("$routeChangeStart", function (event, next, current) {
                /**
                 * Check if the destination route has a property called 'auth'.  If it is
                 * set to 'true', check and prompt for login if needed.
                 */
                //$log.log("$routeChangeStart next route: ", next);
                if ( next.require_auth ) {
                    check_logged_in();
                }
            });

            // Ask user to login when detect the 'event:login:required' event
            $rootScope.$on('event:login:required', function () {
                ask_user_to_login();
            });

            $rootScope.$on('event:login:expired', function () {
                /**
                 * This event is trigger by 401 response from server, meaning that user is
                 * no longer logged in as far as server is concern.  As result, must clear
                 * the cached login credential before proceeding to login page.
                 */
                clear_login_info();
                ask_user_to_login();
            });
        };

        this.check_login = function () {
            /**
             * Function to be used in place of require_auth route parameters.  It will redirect user
             * to login page if not logged in.
             */
            check_logged_in();
        };

        this.login = function (user_id, password, fail) {
            /**
             * Login using the user_id and password.  When this method is called, it will
             * cache the calling URL and will forward to that URL once login is successful.
             * Login failure is communicated using the fail callback function.
             *
             * @user_id: String
             * @password: String
             * @fail: callback
             */
            // Stop $httpProvider.responseInterceptors from capturing 401 while user is attempting to login
            $rootScope.login_in_progress = true;

            // Default POST mapped to add'
            // ToDo: Remove the hard coded /main
            var source_url = get_source_url(),
                loginsvc = new login_service();

            //$log.log("source_url: ", source_url);
            loginsvc.user_id = user_id;
            loginsvc.password = password;
            loginsvc.$login(
                function (data) {
                    if (data.user_id === user_id) {
                        // Set the user as logged in
                        if ( data.user_name ) {
                            logged_in_user = data.user_name;
                        } else {
                            logged_in_user = user_id;
                        }
                        $rootScope.loggedUser = logged_in_user;

                        $log.info('Setting Auth Header To: ',  data.auth_token);
                        // Set the common header
                        set_auth_header(data.auth_token);

                        // Resume capturing of 401 by $httpProvider.responseInterceptors
                        $rootScope.login_in_progress = false;

                        // Redirect to source_url when login succeeds
                        $location.search(source_url_key, null);
                        $location.path(source_url);
                    } else {
                        if (fail) {
                            fail("Returned user '" + data.user_id + "' is not valid");
                        }
                    }
                },
                function (error) {
                    // Report Error
                    if (fail) {
                        fail(error);
                    }
                }
            );
        };

        this.login_oauth = function (provider) {
            /**
             * Login user using OAuth.
             */
            var source_url = get_source_url(),
                oauth_url = "/auth/oauth/" + provider;

            if ( source_url ) {
                oauth_url += "?redirect_url=" + encodeURIComponent("/#" + source_url);
            } else {
                oauth_url += "?redirect_url=" + encodeURIComponent("/#/main");
            }

            $log.log("oauth_url: " + oauth_url);
            // Redirection to a URL not handled by Angular and thus using $window instead of $location
            $window.location = oauth_url;
        };

        this.logout = function (success, fail) {
            /**
             * Call the logout API and expect the server to delete the cookie and logout
             * user from the server.
             */
            var loginsvc = new login_service();
            loginsvc.$logout(
                function (data) {
                    clear_login_info();
                    if (success) {
                        success(data);
                    } else {
                        $location.path("/");
                    }
                },
                function (error) {
                    if (fail) {
                        fail(error);
                    }
                }
            );
        };

        this.get_username = function () {
            /**
             * Return the logged in user.  Essentially, act as primary function to determine
             * if user is logged in or not from webapp perspective.
             *
             * The check start with the logged_in_user.  If it is set, use that.
             */
            if ( logged_in_user ) {
                //$log.log("get_username from variable: logged_in_user");
                return logged_in_user;
            } else {
                var auth_cookie = $cookieStore.get(auth_key);
                if (auth_cookie) {
                    var auth_info = auth_cookie.split(":");
                    if ( auth_info[0] ) {
                        //$log.log("get_username from cookie: ", auth_cookie);
                        logged_in_user = auth_info[0];
                        $rootScope.loggedUser = logged_in_user;
                        set_auth_header(auth_cookie);
                        return logged_in_user;
                    }
                }
                //$log.log("get_username: undefined");
                return undefined;
            }
        };
    })
    .config(function ($httpProvider) {
        /**
         * Unfortunately, there is no way to implement the responseInterceptors logic inside
         * Authenticate.initialize() because:
         *   1. Config Block only allow for provider and constants to be injected, not instances
         *   2. Run block allow for instance and constants to be injected, not providers
         *
         * In other words:
         *   .config allow for $httpProvider but not Authenticate
         *   .run allow for Authenticate but not $httpProvider
         *
         * So, only logic under .run can be moved into the Authenticate service.
         *
         * Reference:
         *   URL: http://docs.angularjs.org/guide/module
         *   Section: "Module Loading & Dependencies"
         */

        // Create a promise to be inserted into http responseInterceptors
        // ref: http://docs.angularjs.org/api/ng.$q
        var inteceptor = ['$rootScope', '$q', function ($rootScope, $q) {
            function success(response) {
                return response;
            };
            function error(response) {
                var status = response.status;
                // $rootScope.login_in_progress is necessary so that login fail can be reported.
                if ( status === 401 && ! $rootScope.login_in_progress ) {
                    $rootScope.$broadcast('event:login:expired');
                    // Return an empty response
                    return { data: "Login Required.", status: 401};
                } else {
                    // Return error, similar to throw response;
                    return $q.reject(response);
                }
            };
            return function(promise) {
                return promise.then(success, error);
            };
        }];
        $httpProvider.responseInterceptors.push(inteceptor);
    });
