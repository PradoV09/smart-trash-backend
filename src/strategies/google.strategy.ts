import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Profile, Strategy, VerifyCallback } from 'passport-google-oauth20';

@Injectable()
export class GoogleStrategy extends PassportStrategy(Strategy, 'google') {
  constructor() {
    super({
      clientID: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_SECRET!,
      callbackURL: process.env.GOOGLE_CALLBACKURL,
      scope: ['profile', 'email'],
      userProfileURL: 'https://www.googleapis.com/oauth2/v3/userinfo',
    });
  }

  async validate(
    accessToken: string,
    refreshToken: string,
    profile: any,
    done: VerifyCallback,
  ) {
    console.log('PROFILE:', profile);

    const user = {
      id: profile.id,
      email: profile.emails?.[0]?.value,
      firstName: profile.name?.givenName,
      lastName: profile.name?.familyName,
      picture: profile.photos?.[0]?.value,
    };

    done(null, user);
  }
}
