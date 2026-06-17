*$ CREATE SOURCE.FOR
*COPY SOURCE
*
*=== source ===========================================================*
*
      SUBROUTINE SOURCE ( NOMORE )

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1990-2006      by    Alfredo Ferrari & Paola Sala  *
*     All Rights Reserved.                                             *
*                                                                      *
*                                                                      *
*     New source for FLUKA9x-FLUKA200x:                                *
*                                                                      *
*     Created on 07 january 1990   by    Alfredo Ferrari & Paola Sala  *
*                                                   Infn - Milan       *
*                                                                      *
*     Last change on 03-mar-06     by    Alfredo Ferrari               *
*                                                                      *
*  This is just an example of a possible user written source routine.  *
*  note that the beam card still has some meaning - in the scoring the *
*  maximum momentum used in deciding the binning is taken from the     *
*  beam momentum.  Other beam card parameters are obsolete.            *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE '(BEAMCM)'
      INCLUDE '(FHEAVY)'
      INCLUDE '(FLKSTK)'
      INCLUDE '(IOIOCM)'
      INCLUDE '(LTCLCM)'
      INCLUDE '(PAPROP)'
      INCLUDE '(SOURCM)'
      INCLUDE '(SUMCOU)'
*
      INCLUDE '(CASLIM)'
*
      DOUBLE PRECISION ENERGY(65000), XYPOS(65000), YXPOS(65000)
      DOUBLE PRECISION ZPOS(65000), FWHMX(65000), FWHMY(65000)
      DOUBLE PRECISION FWHMZ(65000), PART(65000), PSPREAD
      INTEGER NWEIGHT
      DOUBLE PRECISION COSX(65000), COSY(65000), COSZ(65000)
      DOUBLE PRECISION ROOT, DELTAP, SPOTRAND, SPOTSUM
      DOUBLE PRECISION KOEFF1, KOEFF2, KOEFF3, KOEFF4, KOEFF5

      SAVE ENERGY, XYPOS, YXPOS
      SAVE ZPOS, FWHMX, FWHMY
      SAVE FWHMZ, PART, PSPREAD
      SAVE NWEIGHT
      SAVE COSX, COSY, COSZ
      SAVE ROOT, DELTAP
      SAVE KOEFF1, KOEFF2, KOEFF3, KOEFF4, KOEFF5

      LOGICAL LFIRST
*
      SAVE LFIRST
      DATA LFIRST / .TRUE. /
*======================================================================*
*                                                                      *
*                 BASIC VERSION                                        *
*                                                                      *
*======================================================================*
      NOMORE = 0
*  +-------------------------------------------------------------------*
*  |  First call initializations:
      IF ( LFIRST ) THEN
*  |  *** The following 3 cards are mandatory ***

         TKESUM = ZERZER
         LFIRST = .FALSE.
         LUSSRC = .TRUE.

c        treatment field .dat file
         OPEN(44, FILE = '../04_180.dat',
     $        STATUS = 'OLD')
*        Skip first three lines
         READ(44, *)
         READ(44, *)
         READ(44, *)

         NWEIGHT = 0
         WSUM = ZERZER
         DO
            NWEIGHT = NWEIGHT + 1
            IF (NWEIGHT .GT. 65000) THEN
               WRITE(LUNOUT,*) 'SOURCE ERROR: Too many spots'
            ENDIF

            READ (44, 3, END=10 ) ENERGY(NWEIGHT),
     $           XYPOS(NWEIGHT), YXPOS(NWEIGHT), ZPOS(NWEIGHT),
     $           FWHMX(NWEIGHT), FWHMY(NWEIGHT), FWHMZ(NWEIGHT),
     $           PART(NWEIGHT), COSX(NWEIGHT), COSY(NWEIGHT),
     $           COSZ(NWEIGHT)
 3          FORMAT(F12.4,F12.4,F12.4,F12.4,F12.4,F12.4,F12.4,E12.4,
     $                F12.6,F12.6,F12.6)
            WSUM = WSUM + PART(NWEIGHT)

         ENDDO
 10      CONTINUE

         WRITE(LUNOUT,*) 'SOURCE spots found:', NWEIGHT-1
         WRITE(LUNOUT,*) 'SOURCE summed weight (float) :', WSUM

      END IF

*** Sample a beamlet ****************************


*     Choose randomly which spot to sample. It takes into account that each
*     spot/line has a different different weight
      RAND = FLRNDM(DOUBLEDUMMY) ! Returns double precision between [0,1)
      SPOTRAND = WSUM * RAND
      SPOTSUM = ZERZER

      DO I = 1, NWEIGHT ! Loop through lines until SPOTRAND is reached
        SPOTSUM = SPOTSUM + PART(I)
        IF (SPOTSUM .GT. SPOTRAND) THEN
           NRAN = I ! Select the spot
           EXIT
        END IF
      END DO

      ENK = ENERGY(NRAN)
      XBEAM = XYPOS(NRAN)
      YBEAM = YXPOS(NRAN)
      ZBEAM = ZPOS(NRAN)
      XSPOT = FWHMX(NRAN)/2.35482
      YSPOT = FWHMY(NRAN)/2.35482
      ZSPOT = FWHMZ(NRAN)/2.35482
      COSIX = COSX(NRAN)
      COSIY = COSY(NRAN)
      COSIZ = COSZ(NRAN)


*** End of beamlet sample ********************************************


*  +-------------------------------------------------------------------*
*  Push one source particle to the stack. Note that you could as well
*  push many but this way we reserve a maximum amount of space in the
*  stack for the secondaries to be generated
* Npflka is the stack counter: of course any time source is called it
* must be =0
      NPFLKA = NPFLKA + 1
* Wt is the weight of the particle
      WTFLK  (NPFLKA) = ONEONE ! Set weight = 1
c     Sets the weight of the particle
      WEIPRI = WEIPRI + WTFLK (NPFLKA)
c     WEIPRI updates the total weight of the primaries
* Particle type (1=proton.....). Ijbeam is the type set by the BEAM
* card
*  +-------------------------------------------------------------------*
*  |  (Radioactive) isotope:
      IF ( IJBEAM .EQ. -2 .AND. LRDBEA ) THEN
         IARES  = IPROA
         IZRES  = IPROZ
         IISRES = IPROM
         CALL STISBM ( IARES, IZRES, IISRES )
         IJHION = IPROZ  * 1000 + IPROA
         IJHION = IJHION * 100 + KXHEAV
         IONID  = IJHION
         CALL DCDION ( IONID )
         CALL SETION ( IONID )
*  |
*  +-------------------------------------------------------------------*
*  |  Heavy ion:
      ELSE IF ( IJBEAM .EQ. -2 ) THEN
         IJHION = IPROZ  * 1000 + IPROA
         IJHION = IJHION * 100 + KXHEAV
         IONID  = IJHION
         CALL DCDION ( IONID )
         CALL SETION ( IONID )
         ILOFLK (NPFLKA) = IJHION
*  |  Flag this is prompt radiation
         LRADDC (NPFLKA) = .FALSE.
*  |
*  +-------------------------------------------------------------------*
*  |  Normal hadron:
      ELSE
         IONID = IJBEAM
         ILOFLK (NPFLKA) = IJBEAM
*  |  Flag this is prompt radiation
         LRADDC (NPFLKA) = .FALSE.
      END IF
*  |
*  +-------------------------------------------------------------------*
* From this point .....
* Particle generation (1 for primaries)
      LOFLK  (NPFLKA) = 1
* User dependent flag:
      LOUSE  (NPFLKA) = 0
*  No channeling:
      KCHFLK (NPFLKA) = 0
      ECRFLK (NPFLKA) = ZERZER
* User dependent spare variables:
      DO 100 ISPR = 1, MKBMX1
         SPAREK (ISPR,NPFLKA) = ZERZER
 100  CONTINUE
* User dependent spare flags:
      DO 200 ISPR = 1, MKBMX2
         ISPARK (ISPR,NPFLKA) = 0
 200  CONTINUE
* Save the track number of the stack particle:
      ISPARK (MKBMX2,NPFLKA) = NPFLKA
      NPARMA = NPARMA + 1
      NUMPAR (NPFLKA) = NPARMA
      NEVENT (NPFLKA) = 0
      DFNEAR (NPFLKA) = +ZERZER
* ... to this point: don't change anything
* Particle age (s)
      AGESTK (NPFLKA) = +ZERZER
      AKNSHR (NPFLKA) = -TWOTWO
* Group number for "low" energy neutrons, set to 0 anyway
      IGROUP (NPFLKA) = 0
****************************************************************

*     Sample a gaussian position
      CALL FLNRR2 (RGAUS1, RGAUS2)
      XFLK   (NPFLKA) = XBEAM + XSPOT * RGAUS1
      YFLK   (NPFLKA) = YBEAM + YSPOT * RGAUS2
      CALL FLNRRN (RGAUSS)
      ZFLK   (NPFLKA) = ZBEAM + ZSPOT * RGAUSS

*     Cosines (tx,ty,tz)
      ROOT = SQRT(COSIX**2+COSIY**2+COSIZ**2)
      TXFLK  (NPFLKA) = COSIX/ROOT
      TYFLK  (NPFLKA) = COSIY/ROOT
      TZFLK  (NPFLKA) = COSIZ/ROOT
*     TZFLK  (NPFLKA) = SQRT ( ONEONE - TXFLK (NPFLKA)**2
*    &                       - TYFLK (NPFLKA)**2 )
*********************************************************************
*     Particle momentum
*     PMOFLK (NPFLKA) = PBEAM
      CALL FLNRRN(RGAUSS)
      PMOFLK (NPFLKA) = SQRT ( ENK* ( ENK
     &     + TWOTWO * AM (IONID) ))

*     Calculate momentum spread using third polynomial fit
      KOEFF1 = 15.15869
      KOEFF2 = 13.25411
      KOEFF3 = 4.08560
      KOEFF4 = 0.40984
      KOEFF5 = 0.00394

      DELTAP = -KOEFF1*ENK**4 + KOEFF2*ENK**3
     &          - KOEFF3*ENK**2 + KOEFF4*ENK + KOEFF5
*      DELTAP = -0.1*ENK+0.024

      PSPREAD = PMOFLK (NPFLKA) * DELTAP / 2.35482 * RGAUSS

      PMOFLK (NPFLKA) = PMOFLK (NPFLKA) + PSPREAD

*     Kinetic energy of the particle (GeV)
*     Set energy
      TKEFLK (NPFLKA) = SQRT(PMOFLK(NPFLKA)**2 + AM(IONID)**2)
     &      -AM(IONID)


*     Polarization cosines:
      TXPOL  (NPFLKA) = -TWOTWO
      TYPOL  (NPFLKA) = +ZERZER
      TZPOL  (NPFLKA) = +ZERZER

*++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
*++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
*     Calculate the total kinetic energy of the primaries: don't change
      IF ( ILOFLK (NPFLKA) .EQ. -2 .OR. ILOFLK (NPFLKA) .GT. 100000 )
     &   THEN
         TKESUM = TKESUM + TKEFLK (NPFLKA) * WTFLK (NPFLKA)
      ELSE IF ( ILOFLK (NPFLKA) .NE. 0 ) THEN
         TKESUM = TKESUM + ( TKEFLK (NPFLKA) + AMDISC (ILOFLK(NPFLKA)) )
     &          * WTFLK (NPFLKA)
      ELSE
         TKESUM = TKESUM + TKEFLK (NPFLKA) * WTFLK (NPFLKA)
      END IF
      RADDLY (NPFLKA) = ZERZER

*  Here we ask for the region number of the hitting point.
*     NREG (NPFLKA) = ...
*  The following line makes the starting region search much more
*  robust if particles are starting very close to a boundary:
      CALL GEODRR ( TXFLK (NPFLKA), TYFLK (NPFLKA), TZFLK (NPFLKA) )
      CALL GEOREG ( XFLK  (NPFLKA), YFLK  (NPFLKA), ZFLK  (NPFLKA),
     &              NRGFLK(NPFLKA), IDISC )
*      WRITE(LUNOUT,*) 'NB SOURCE mark2'
*  Do not change these cards:
      CALL GEOHSM ( NHSPNT (NPFLKA), 1, -11, MLATTC )
      NLATTC (NPFLKA) = MLATTC
      CMPATH (NPFLKA) = ZERZER
      CALL SOEVSV

      CLOSE(44)
      RETURN
*=== End of subroutine Source =========================================*
      END
