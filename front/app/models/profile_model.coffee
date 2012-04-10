class exports.ProfileModel extends Backbone.Model
  urlRoot: '/account/profiles/'

  initialize: ->
    @front =
      edit: "/#!/profiles/#{@id}/edit"
      show: "/#!/profiles/#{@id}"

  getUsername: ->
    [first, last] = [@get('first_name'), @get('last_name')]
    username = $.trim "#{first? and first or ''} #{last? and last or ''}"
    username = username.length and username or "please, fill your profile data"
    username
