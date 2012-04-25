class exports.SessionModel extends Backbone.Model
    urlRoot: '/account/sessions/'

    emailRegex: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/,

    defaults:
      is_anonymous: true


class exports.LoginModel extends exports.SessionModel
  defaults:
    email: ''
    password: ''

  validate: (attrs) ->
    response =
      status: 'success'
    console.log attrs.email, @emailRegex.test attrs.email
    if !@emailRegex.test(attrs.email)
      response.status = 'failed'
      response.email = 'This is not valid email address'
      console.log 'email failed'
    if attrs.password.length is 0
      response.status = 'failed'
      response.password = 'You forgot to specify password'
    if response.status == 'failed'
      return response
