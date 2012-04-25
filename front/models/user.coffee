define [
    'chaplin/model'
], (Model) ->
  'use strict'

  class User extends Model

    emailRegex: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/,

    defaults:
      email: ''

    initialize: ->
      console.log "User#initialize", @urlRoot

    validate: (attrs) ->
      response =
        status: 'success'

      console.log "User#validate", attrs.email, @emailRegex.test attrs.email

      unless @emailRegex.test(attrs.email)
        response.status = 'failed'
        response.email = 'This is not valid email address'
        response
