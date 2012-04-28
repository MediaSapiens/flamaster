define [
  'chaplin/mediator', 'chaplin/lib/utils', 'chaplin/lib/services/service_provider'
], (mediator, utils, ServiceProvider) ->
  'use strict'

  class Custom extends ServiceProvider
    name: 'custom'

    # Login status at Facebook
    status: null

    # The current session API access token
    accessToken: null

    sessionId: null

    constructor: ->
      super
      console.debug 'Custom#constructor'
      @subscribeEvent 'logout', @logout

    dispose: ->
      # TODO unsubscribe

    # Load the JavaScript SDK asynchronously
    loadSDK: -> @resolve()

    # Check whether the SDK has been loaded
    isLoaded: -> true

    # Save the current login status and the access token
    # (if logged in and connected with app)
    saveAuthResponse: (response) =>
      console.debug 'Custom#saveAuthResponse', response
      @status = !response.is_anonymous
      @sessionId = response.id

    # Get the Facebook login status, delegates to FB.getLoginStatus
    #
    # This actually determines a) whether the user is logged in at Facebook
    # and b) whether the user has authorized the app
    getLoginStatus: (callback = @loginStatusHandler, force = false) =>
      console.debug 'Custom#getLoginStatus'
      response = $.get '/account/sessions/'
      response.success callback

    # Callback for the initial FB.getLoginStatus call
    loginStatusHandler: (response) =>
      console.debug 'Custom#loginStatusHandler', response
      @saveAuthResponse response
      authResponse = response.is_anonymous
      unless authResponse
        @publishSession response.id
        @getUserData()
      else
        mediator.publish 'logout'

    # loginContext: object with context information where the
    # user triggered the login
    #   Attributes:
    #   description - string
    #   model - optional model e.g. a topic the user wants to subscribe to
    triggerLogin: (loginContext) ->
      console.debug 'Custom#triggerLogin', loginContext, @sessionId
      $.ajax
        url: "/account/sessions/#{@sessionId}"
        contentType: 'application/json'
        type: 'put'
        data: JSON.stringify(loginContext)
        processData: false
        complete: _(@loginHandler).bind(@)

    # Callback for FB.login
    loginHandler: (loginContext, status) =>
      console.debug 'Custom#loginHandler', loginContext, status
      switch status
        when 'error' then mediator.publish 'loginAbort', JSON.parse(loginContext.responseText)

      # @saveAuthResponse response
      # authResponse = response.authResponse

      # if authResponse
      #   mediator.publish 'loginSuccessful', {provider: this, loginContext}
      #   @publishSession authResponse
      #   @getUserData()

      # else
      #   mediator.publish 'loginAbort', {provider: this, loginContext}

        # Get the login status again (forced) because the user might be
        # logged in anyway. This might happen when the user grants access
        # to the app but closes the second page of the auth dialog which
        # asks for Extended Permissions.
      #   @getLoginStatus @publishAbortionResult, true

    # Publish the Facebook session
    publishSession: (authResponse) ->
      console.debug 'Custom#publishSession', authResponse
      mediator.publish 'serviceProviderSession',
        provider: this
        userId: authResponse.userID
        accessToken: authResponse.accessToken

    # Check login status after abort and publish success or failure
    publishAbortionResult: (response) =>
      @saveAuthResponse response
      authResponse = response.authResponse

      if authResponse
        mediator.publish 'loginSuccessful', {provider: this, loginContext}
        mediator.publish 'loginSuccessfulThoughAborted', {
          provider: this, loginContext
        }

        @publishSession authResponse

      else
        # Login failed ultimately
        mediator.publish 'loginFail', {provider: this, loginContext}

    # Handler for the global logout event
    logout: ->
      # Clear the status properties
      @status = @accessToken = null


    #
    # Graph Querying
    # --------------

    getUserData: ->
      console.debug 'Custom#getUserData'
      # @getInfo '/me', @processUserData

    processUserData: (response) =>
      #console.debug 'Facebook#processUserData', response
      mediator.publish 'userData', response
