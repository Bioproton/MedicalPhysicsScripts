*$ CREATE FLUSCW.FOR
*COPY FLUSCW
*
*=== fluscw ===========================================================*
*                                                                      *
      DOUBLE PRECISION FUNCTION FLUSCW ( IJ    , PLA   , TXX   , TYY   ,
     &                                   TZZ   , WEE   , XX    , YY    ,
     &                                   ZZ    , NREG  , IOLREG, LLO   ,
     &                                   NSURF )

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1989-2005      by    Alfredo Ferrari & Paola Sala  *
*     All Rights Reserved.                                             *
*                                                                      *
*     New version of Fluscw for FLUKA9x-FLUKA200x:                     *
*                                                                      *
*     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!     *
*     !!! This is a completely dummy routine for Fluka9x/200x. !!!     *
*     !!! The  name has been kept the same as for older  Fluka !!!     *
*     !!! versions for back-compatibility, even though  Fluscw !!!     *
*     !!! is applied only to estimators which didn't exist be- !!!     *
*     !!! fore Fluka89.                                        !!!     *
*     !!! User  developed versions  can be used for  weighting !!!     *
*     !!! flux-like quantities at runtime                      !!!     *
*     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!     *
*                                                                      *
*     Input variables:                                                 *
*                                                                      *
*           Ij = (generalized) particle code (Paprop numbering)        *
*          Pla = particle laboratory momentum (GeV/c) (if > 0),        *
*                or kinetic energy (GeV) (if <0 )                      *
*    Txx,yy,zz = particle direction cosines                            *
*          Wee = particle weight                                       *
*     Xx,Yy,Zz = position                                              *
*         Nreg = (new) region number                                   *
*       Iolreg = (old) region number                                   *
*          Llo = particle generation                                   *
*        Nsurf = transport flag (ignore!)                              *
*                                                                      *
*     Output variables:                                                *
*                                                                      *
*       Fluscw = factor the scored amount will be multiplied by        *
*       Lsczer = logical flag, if true no amount will be scored        *
*                regardless of Fluscw                                  *
*                                                                      *
*     Useful variables (common SCOHLP):                                *
*                                                                      *
*     Flux like binnings/estimators (Fluscw):                          *
*          ISCRNG = 1 --> Boundary crossing estimator                  *
*          ISCRNG = 2 --> Track  length     binning                    *
*          ISCRNG = 3 --> Track  length     estimator                  *
*          ISCRNG = 4 --> Collision density estimator                  *
*          ISCRNG = 5 --> Yield             estimator                  *
*          JSCRNG = # of the binning/estimator                         *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE '(SCOHLP)'
      INCLUDE '(FLKMAT)'
      INCLUDE '(FHEAVY)'
      INCLUDE '(PAPROP)'
      INCLUDE '(USRBIN)'
      INCLUDE '(TRACKR)'
      INCLUDE '(CASLIM)'

*----------------------------------------------------------------------*
* 3 Tables are created to imported the Belli data, one for energy      *
* (BETAB), one for RBE_max (BXTAB) and one for RBE_min (BNTAB).        *
* BETAB = Belli Energy TABle                                           *
* BXTAB = Belli rbe_maX TABle                                          *
* BNTAB = Belli rbe_miN TABle                                          *

      PARAMETER (NBEL   = 15)
c      PARAMETER (GEVGRA = 1.602176462D-7) !uncomment if FLUKA 2011

      DIMENSION BETAB(NBEL)
      DIMENSION BXTAB(NBEL)
      DIMENSION BNTAB(NBEL)

      REAL(8) :: BETAB
      REAL(8) :: BXTAB
      REAL(8) :: BNTAB

*----------------------------------------------------------------------*
* The LFIRST variable is used to initialize global values              *

      LOGICAL LFIRST
      SAVE LFIRST
      DATA LFIRST / .TRUE. /

*----------------------------------------------------------------------*
* The LSCOND variable is used to run thru all scorecards for the first *
* check whether the belli model is included in the simulations,        *

      LOGICAL LSCOND
      SAVE LSCOND
      DATA LSCOND / .FALSE. /

      IF ( LFIRST ) THEN
* Used to check if all scorecards has been run through
         IF(JSCRNG.EQ.1 .AND. LSCOND) THEN
            LFIRST = .FALSE.
         ENDIF
         LSCOND = .TRUE.

* Load the Bellimodel, as given in the .dat file
         IF(IPUSBN(JSCRNG).EQ.-65 .OR. IPUSBN(JSCRNG).EQ.-66) THEN
            CALL OAUXFI('../Belli_RBEtable.dat', 99, 'OLD', IERR)
            IF ( IERR .GT. 0 ) STOP 'FILE NOT FOUND'
            DO J=1,NBEL
            READ (99,*)BETAB(J),BXTAB(J),BNTAB(J)
            END DO
            CLOSE(UNIT=99)
         ENDIF

* Find Water in geometry, needed for scoring dose to water
         DO I=1, NMAT
            IF  (MATNAM(I) .EQ. 'WATER') THEN
               MATW = I
            END IF
         END DO

*----------------------------------------------------------------------*
* Set Alpha/Beta Ratios (ABRAT1 is default) ABRAT1 corresponds to       *
* bin number 60 and 70, ABRAT2 to binnumber 61 and 71. More             *
* ratios/scorecards can be added if wanted.                            *

         ABRAT1 = 2.1
         ABRAT2 = 2.5
         ABRAT3 = 3.3


* TDELTA sets the energy restriction for the LET scoring. -ONEONE      *
* corresponds to unrestricted LET.                                     *
         TDELTA=-ONEONE

      END IF

      FLUSCW = ZERZER
      LSCZER = .FALSE.

      IF(IJ.LT.-6)THEN
         AMPART = AMNHEA(-IJ)
         ICPART = ICHEAV(-IJ)
         IF(PLA.LT.ZERZER)THEN
            EKPART=ABS(PLA)
            PLA=SQRT(EKPART*(EKPART+TWOTWO*AMPART))
         ELSE
            EKPART = SQRT ( PLA**2 + AMPART**2 ) - AMPART
         END IF
      ELSEIF((IJ.EQ.1).OR.((IJ.LE.-2).AND.(IJ.GE.-6)))THEN
         AMPART = AM(IJ)
         ICPART = ICHRGE(IJ)
         IF(PLA.LT.ZERZER)THEN
            EKPART=ABS(PLA)
            PLA=SQRT(EKPART*(EKPART+TWOTWO*AMPART))
         ELSE
            EKPART = SQRT ( PLA**2 + AMPART**2 ) - AMPART
         END IF
      ELSE
         AMPART = AM(IJ)
         ICPART = 0
         IF(PLA.LT.ZERZER)THEN
            EKPART=ABS(PLA)
            PLA=SQRT(EKPART*(EKPART+TWOTWO*AMPART))
         ELSE
            EKPART = SQRT ( PLA**2 + AMPART**2 ) - AMPART
         END IF
      END IF

* Different scorecards:

      IF(EKPART.LT.AZRZRZ)THEN
         FLUSCW =  ZERZER
      ELSE
         ALETW = GETLET(IJ,EKPART,PLA,TDELTA,MATW)
         GLETW = ALETW/1.D+2
* Calculate dose to water for protons (40) or all particles (50)
*        Only protons (40) and all part (50)
         IF(IPUSBN(JSCRNG).EQ.-40 .OR. IPUSBN(JSCRNG).EQ.-50) THEN
            FLUSCW =GLETW*GEVGRA
            RETURN
* Calculate LET to water for protons (41) or all particles (51)
         ELSE IF(IPUSBN(JSCRNG).EQ.-41 .OR. IPUSBN(JSCRNG).EQ.-51) THEN
            FLUSCW =GLETW*GEVGRA*ALETW
            RETURN

*----------------------------------------------------------------------*
* Non-linear biological models. Calculate the RBE_max(or sqrt(RBE_min))*
* times dose to water for different nonlinear models.                  *
* All non-linear biological models are only able to calculate RBE for a*
* single alpha/beta ratio for a scorer.                                *
* The RBE_max of the Mairani model and the Bergen model is dependent of*
* alpha/beta ratio, therefore multiple scorecards are need for multiple*
* ratios.                                                              *

* Bergen model:
*RBE_max times proton dose to water (60-64, defualt 60). Dose to water *
* for protons (40) also needs to be calculated.                        *
         ELSE IF(IPUSBN(JSCRNG).EQ.-60) THEN
            IF(ALETW.LT.37) THEN
                BER1 = 0.578*ALETW-0.0808*ALETW**2
                BER2 = 0.00564*ALETW**3-0.0000992*ALETW**4
                ARBEBER = 1 + (1/ABRAT1)*(BER1+BER2)
            ELSE
                ARBEBER = 1 + 10.5/ABRAT1
            ENDIF
            FLUSCW = ARBEBER*GLETW*GEVGRA
            RETURN
         ELSE IF(IPUSBN(JSCRNG).EQ.-61) THEN
            IF(ALETW.LT.37) THEN
                BER1 = 0.578*ALETW-0.0808*ALETW**2
                BER2 = 0.00564*ALETW**3-0.0000992*ALETW**4
                ARBEBER = 1 + (1/ABRAT2)*(BER1+BER2)
            ELSE
                ARBEBER = 1 + 10.5/ABRAT2
            ENDIF
            FLUSCW = ARBEBER*GLETW*GEVGRA
            RETURN
         ELSE IF(IPUSBN(JSCRNG).EQ.-62) THEN
            IF(ALETW.LT.37) THEN
                BER1 = 0.578*ALETW-0.0808*ALETW**2
                BER2 = 0.00564*ALETW**3-0.0000992*ALETW**4
                ARBEBER = 1 + (1/ABRAT3)*(BER1+BER2)
            ELSE
                ARBEBER = 1 + 10.5/ABRAT3
            ENDIF
            FLUSCW = ARBEBER*GLETW*GEVGRA
            RETURN


* Mairani model:
*----------------------------------------------------------------------*
*RBE_max times all particles dose to water (70-74, defualt 70). Dose to*
* water for all part (50) also needs to be calculated.                 *
         ELSE IF(IPUSBN(JSCRNG).EQ.-70) THEN
            IF(IJ.EQ.1 .OR. IJ.EQ.-3 .OR. IJ.EQ.-4) THEN
               ARBEMAI = 1 + 0.377/ABRAT1*ALETW
            ELSE IF(IJ.EQ.-5 .OR. IJ.EQ.-6) THEN
               AMAIBXP = 0.336790*ALETW*EXP(-0.0000285738*ALETW*ALETW)
               ARBEMAI = 1 + (0.0892375+1/ABRAT1)*AMAIBXP
            ELSE
               ARBEMAI = 0
            ENDIF
            FLUSCW = ARBEMAI*GLETW*GEVGRA
            RETURN
         ELSE IF(IPUSBN(JSCRNG).EQ.-71) THEN
            IF(IJ.EQ.1 .OR. IJ.EQ.-3 .OR. IJ.EQ.-4) THEN
               ARBBMAI = 1 + 0.377/ABRAT2*ALETW
            ELSE IF(IJ.EQ.-5 .OR. IJ.EQ.-6) THEN
               AMAIBXP = 0.336790*ALETW*EXP(-0.0000285738*ALETW*ALETW)
               ARBEMAI = 1 + (0.0892375+1/ABRAT2)*MAIBXP
            ELSE
               ARBEMAI = 0
            ENDIF
            FLUSCW = ARBEMAI*GLETW*GEVGRA
            RETURN


* These two models are included as a reference/template for creating
* other models:
* Belli model:
*----------------------------------------------------------------------*
* RBE_max times proton dose to water(65). Dose to water for protons(40)*
* also needs to be calculated as well.                                 *
         ELSE IF(IPUSBN(JSCRNG).EQ.-65) THEN
            EPRAMU = (EKPART* AMUGEV / AMPART)*GEVMEV
            ARBEMAX = ABVALUE(EPRAMU,BETAB,BXTAB,NBEL)
            FLUSCW = ARBEMAX*GLETW*GEVGRA
            RETURN
* RBE_min times proton dose to water(66). Dose to water for protons(40)*
* also needs to be calculated as well.                                 *
         ELSE IF(IPUSBN(JSCRNG).EQ.-66) THEN
            EPRAMU = (EKPART* AMUGEV / AMPART)*GEVMEV
            ARBEMIN = ABVALUE(EPRAMU,BETAB,BNTAB,NBEL)
            FLUSCW = SQRT(ARBEMIN)*GLETW*GEVGRA
            RETURN

* Unkelbach model:
*----------------------------------------------------------------------*
* RBE_max times proton dose to water(67). Dose to water for protons(40)*
* also needs to be calculated as well.                                 *
         ELSE IF(IPUSBN(JSCRNG).EQ.-67) THEN
            ARBEMAX = 1*0.04*ALETW
            FLUSCW = ARBEMAX*GLETW*GEVGRA
            RETURN
* RBE_min times proton dose to water(68). Dose to water for protons(40)*
* also needs to be calculated as well.                                 *
         ELSE IF(IPUSBN(JSCRNG).EQ.-68) THEN
            ARBEMAX = 1*0.04*ALETW
            FLUSCW = ARBEMIN*GLETW*GEVGRA
            RETURN

         ELSE
            FLUSCW = ONEONE
         ENDIF
      ENDIF
      RETURN
*===  End of function Fluscw ===========================================*
      END


*$ CREATE ABVALUE.FOR
*COPY ABVALUE
      DOUBLE PRECISION FUNCTION ABVALUE (XVALUE,XARRAY,YARRAY,IDIMEN)
*----------------------------------------------------------------------*
*     Interpolate the value of alphaD or betaD from the tables,
*     and it gives back the min if you Energy/u is lower than the min
*     or the max value if your energy/u is larger than the max
*----------------------------------------------------------------------*

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      DIMENSION XARRAY(IDIMEN),YARRAY(IDIMEN)

      IF(XVALUE.GE.XARRAY(IDIMEN))THEN
         ABVALUE = YARRAY(IDIMEN)
      ELSEIF((XVALUE .LE. XARRAY(1)))THEN
         ABVALUE = YARRAY(1)
      ELSE
         ABVALUE = YINTLG(XVALUE,XARRAY,YARRAY,IDIMEN)
      ENDIF
      RETURN
*=== End of Function Abvalue ============================================*
      END

*$ CREATE YINTLG.FOR
*COPY YINTLG
      DOUBLE PRECISION FUNCTION YINTLG(XVALUE,XARRAY,YARRAY,IDIMEN)
*----------------------------------------------------------------------*
*                                                                      *
*    Interpolation of a value Y in corrispondence of an abscissa X     *
*    given an array of abscissae XARRAY and one of ordinates YARRAY.   *
*    IDIMEN is the dimension of the two arrays.                        *
*    If XVALUE is outside range, returns zero.                         *
*    Version for logarithmic interpolation in X                        *
*----------------------------------------------------------------------*
      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      DIMENSION XARRAY(IDIMEN),YARRAY(IDIMEN)

      DO 1 I = 2, IDIMEN
        IF(XVALUE .GE. XARRAY(I-1) .AND. XVALUE .LE. XARRAY(I)) THEN
          K = I
          GO TO 2
        ENDIF
   1  CONTINUE
      YINTLG = 0.D0         !  Outside tabulation range, set to zero
      RETURN
   2  CONTINUE
      XA1 = LOG(XARRAY(K-1))
      XA2 = LOG(XARRAY(K))
      XA  = LOG(XVALUE)
      YINTLG = YARRAY(K-1) + (YARRAY(K) - YARRAY(K-1))*(XA - XA1)
     &                                              / (XA2 - XA1)
      RETURN
*=== End of Function Yintlg ===========================================*
      END
