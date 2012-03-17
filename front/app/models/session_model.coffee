class exports.SessionModel extends Backbone.Model
    urlRoot: '/account/sessions/',
    emailRegex: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/,

    validate: (attrs) ->
      response =
        status: 'success'

      if !this.emailRegex.test(attrs.email)
        response.status = 'failed'
        response.email = 'This is not valid email address'
      if attrs.password isnt attrs.confirm
        response.status = 'failed'
        response.confirm = "Confirmation don't match"

      if response.status == 'failed'
        return response

    is_anonymous: ->
      console.log this.toJSON()
