class exports.SessionModel extends Backbone.Model
    urlRoot: '/account/sessions/'

    emailRegex: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/,

    initial:
      is_anonymous: true

    save: ->
      console.log 'save', arguments
      super arguments


class exports.LoginModel extends exports.SessionModel
  defaults:
    email: ''
    password: ''

  validate: (attrs) ->
    response =
      status: 'success'
    if !this.emailRegex.test(attrs.email)
      response.status = 'failed'
      response.email = 'This is not valid email address'
    if attrs.password.length is 0
      response.status = 'failed'
      response.password = 'You forgot to specify password'
    if response.status == 'failed'
      return response
