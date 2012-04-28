define [
    'chaplin/model'
], (Model) ->
  'use strict'

  class User extends Model

    emailRegex: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/,
    urlRoot: '/account/profiles/'
    defaults:
      email: ''

    initialize: ->
      console.log "User#initialize", @urlRoot

    validate: (attrs) ->
      response = status: 'success'

      unless @emailRegex.test(attrs.email)
        response = status: 'failed', email: 'This is not valid email address'

      return response.status isnt 'success' and response or null
