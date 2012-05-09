define [
  'chaplin/mediator',
  'models/base_user'
], (mediator, BaseUser) ->
  'use strict'

  class User extends BaseUser
    urlRoot: '/account/profiles/'

    validate: (attrs) ->
      response = status: 'success'

      for attr in ['first_name', 'last_name', 'phone']
        if attrs[attr].length is 0
          response.status = 'failed'
          response[attr] = "Can't be zero-length"

      if attrs.password.length < 6
        _(response).extend status: 'failed', password: "Password should be more than 5 symbols"

      if attrs.password.length and (attrs.password isnt attrs.password_confirm)
        _(response).extend status: 'failed', password: "Password and confirmation don't match"

      return response.status isnt 'success' and response or null
